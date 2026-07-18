import { useState, useEffect } from "react";
import { Search, SearchX, User, ShieldAlert, Camera, CheckCircle, XCircle, Video, ShieldCheck, Database, Calendar } from "lucide-react";
import { STATE, ACCENT, type DonorVerifyResponse } from "../types";
import { verifyDonor, enrollDonor, getRecentDonors, type EnrolledDonor } from "../services/api";
import Glass from "../components/Glass";

const LOCKOUT_DAYS = 56;

export interface VerificationPageProps {
  openAlert?: () => void;
}

/**
 * Premium Live Biometric Verification page component.
 * Interacts directly with the SQLite database and SFace/YuNet AI models.
 */
export default function Verification() {
  const [query, setQuery] = useState("");
  const [enrollName, setEnrollName] = useState("Donor 1");
  const [b64Image, setB64Image] = useState("");
  const [fileName, setFileName] = useState("");
  const [liveLoading, setLiveLoading] = useState(false);
  const [liveResult, setLiveResult] = useState<DonorVerifyResponse | null>(null);
  const [liveError, setLiveError] = useState<string | null>(null);
  const [enrollStatus, setEnrollStatus] = useState<string | null>(null);

  // Live database records
  const [realDonors, setRealDonors] = useState<EnrolledDonor[]>([]);
  const [donorsLoading, setDonorsLoading] = useState(true);

  // Webcam integration states
  const [isWebcamActive, setIsWebcamActive] = useState(false);
  const [webcamStream, setWebcamStream] = useState<MediaStream | null>(null);

  const fetchRealDonors = async () => {
    setDonorsLoading(true);
    try {
      const list = await getRecentDonors();
      setRealDonors(list);
      // Auto-increment naming
      if (list && list.length > 0) {
        const maxId = Math.max(...list.map(d => d.id));
        setEnrollName(`Donor ${maxId + 1}`);
      } else {
        setEnrollName("Donor 1");
      }
    } catch (err) {
      console.error("Failed to load real donors from gateway:", err);
    } finally {
      setDonorsLoading(false);
    }
  };

  useEffect(() => {
    fetchRealDonors();
    // Cleanup stream on component unmount
    return () => {
      if (webcamStream) {
        webcamStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [webcamStream]);

  const startWebcam = async () => {
    setLiveResult(null);
    setLiveError(null);
    setEnrollStatus(null);
    setB64Image("");
    setFileName("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 320, height: 240, facingMode: "user" }
      });
      setWebcamStream(stream);
      setIsWebcamActive(true);
      
      setTimeout(() => {
        const video = document.getElementById("webcamVideo") as HTMLVideoElement;
        if (video) {
          video.srcObject = stream;
        }
      }, 100);
    } catch (err) {
      console.error("Webcam error:", err);
      alert("Failed to access camera. Please allow camera permissions.");
    }
  };

  const stopWebcam = () => {
    if (webcamStream) {
      webcamStream.getTracks().forEach((track) => track.stop());
      setWebcamStream(null);
    }
    setIsWebcamActive(false);
  };

  const capturePhoto = () => {
    const video = document.getElementById("webcamVideo") as HTMLVideoElement;
    const canvas = document.getElementById("webcamCanvas") as HTMLCanvasElement;
    if (video && canvas) {
      const ctx = canvas.getContext("2d");
      if (ctx) {
        canvas.width = video.videoWidth || 320;
        canvas.height = video.videoHeight || 240;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL("image/jpeg");
        setB64Image(dataUrl.split(",")[1]);
        setFileName("webcam_capture.jpg");
        stopWebcam();
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setLiveResult(null);
    setLiveError(null);
    setEnrollStatus(null);
    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result as string;
      setB64Image(result.split(",")[1]);
    };
    reader.readAsDataURL(file);
  };

  const handleVerify = async () => {
    if (!b64Image) return;
    setLiveLoading(true);
    setLiveResult(null);
    setLiveError(null);
    try {
      const res = await verifyDonor(b64Image);
      setLiveResult(res);
    } catch (err: any) {
      console.error(err);
      setLiveError(err.message || "Failed to complete face verification.");
    } finally {
      setLiveLoading(false);
    }
  };

  const handleEnroll = async () => {
    if (!b64Image || !enrollName) return;
    setLiveLoading(true);
    setEnrollStatus(null);
    try {
      const res = await enrollDonor(enrollName, b64Image);
      setEnrollStatus(`Success! Enrolled '${enrollName}' with ID: ${res.id}`);
      
      // Clear capture and trigger dynamic database reload
      setFileName("");
      setB64Image("");
      await fetchRealDonors();
    } catch (err: any) {
      console.error(err);
      setEnrollStatus(`Enrollment Error: ${err.message || "Failed to reach gateway"}`);
    } finally {
      setLiveLoading(false);
    }
  };

  const filtered = realDonors.filter((d) =>
    d.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-6 p-6 animate-none">
      <style>{`
        @keyframes scanline {
          0% { top: 0%; }
          50% { top: 100%; }
          100% { top: 0%; }
        }
        .scanner-container::after {
          content: '';
          position: absolute;
          left: 0;
          right: 0;
          height: 3px;
          background: linear-gradient(180deg, rgba(47, 217, 196, 0) 0%, #2fd9c4 70%, rgba(47, 217, 196, 0) 100%);
          box-shadow: 0 0 10px #2fd9c4;
          animation: scanline 2.5s linear infinite;
          z-index: 10;
        }
        .scanner-corner {
          position: absolute;
          width: 12px;
          height: 12px;
          border-color: #2fd9c4;
          border-width: 2px;
          z-index: 20;
        }
      `}</style>

      {/* Live Biometric Test Desk */}
      <Glass className="p-5 animate-none relative overflow-hidden" style={{ borderLeft: `3px solid ${ACCENT}` }}>
        <div className="absolute top-0 right-0 p-2 text-[10px] text-teal-400 font-mono tracking-wider flex items-center gap-1.5 bg-[rgba(47,217,196,0.05)] border-b border-l border-[rgba(47,217,196,0.1)] rounded-bl-lg">
          <Database size={10} /> SQLite SYNCED
        </div>

        <h2 className="mb-1.5 flex items-center gap-2 text-sm font-semibold text-white">
          <Camera size={15} style={{ color: ACCENT }} /> Live Biometric Verification Desk
        </h2>
        <p className="mb-5 text-[11px] text-[#8A97A6] leading-normal">
          Real-time face landmark verification and SQLite lockout synchronization via OpenCV YuNet/SFace on Snapdragon NPU.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="mb-4">
              <div className="mb-2 flex items-center justify-between">
                <label className="block text-xs font-semibold" style={{ color: "#8A97A6" }}>Donor Photo Source</label>
                <div className="flex gap-2">
                  {!isWebcamActive && (
                    <button 
                      onClick={startWebcam} 
                      className="flex items-center gap-1 rounded-md px-2.5 py-1 text-[10px] font-semibold text-white border border-[rgba(255,255,255,0.15)] hover:bg-[rgba(255,255,255,0.05)] cursor-pointer transition-colors"
                    >
                      <Video size={10} /> Open Camera
                    </button>
                  )}
                  {isWebcamActive && (
                    <button 
                      onClick={stopWebcam} 
                      className="rounded-md px-2.5 py-1 text-[10px] font-semibold text-[#f87171] border border-[rgba(248,113,113,0.15)] hover:bg-[rgba(248,113,113,0.05)] cursor-pointer transition-colors"
                    >
                      Close Camera
                    </button>
                  )}
                </div>
              </div>
              
              {isWebcamActive ? (
                <div className="scanner-container relative rounded-lg border overflow-hidden flex flex-col items-center bg-[#06080c] h-[160px]" style={{ borderColor: "rgba(47, 217, 196, 0.2)" }}>
                  {/* Glowing camera corners */}
                  <div className="scanner-corner border-t border-l top-2 left-2" />
                  <div className="scanner-corner border-t border-r top-2 right-2" />
                  <div className="scanner-corner border-b border-l bottom-2 left-2" />
                  <div className="scanner-corner border-b border-r bottom-2 right-2" />
                  
                  <video id="webcamVideo" autoPlay playsInline muted className="w-full h-full object-cover bg-black opacity-80" />
                  <button 
                    onClick={capturePhoto} 
                    className="absolute bottom-2 rounded-full px-4 py-1.5 text-[10px] font-bold text-black cursor-pointer shadow-lg hover:scale-105 active:scale-95 transition-transform"
                    style={{ background: ACCENT, boxShadow: "0 0 10px rgba(47,217,196,0.4)" }}
                  >
                    Capture Photo
                  </button>
                  <canvas id="webcamCanvas" className="hidden" />
                </div>
              ) : (
                <div 
                  onClick={() => document.getElementById("liveFaceFile")?.click()}
                  className="border-2 border-dashed border-[rgba(255,255,255,0.08)] hover:border-[#2fd9c4] rounded-lg p-6 text-center cursor-pointer transition-colors flex flex-col items-center justify-center gap-1 min-h-[160px] bg-[rgba(255,255,255,0.01)] hover:bg-[rgba(47,217,196,0.02)]"
                >
                  <Camera size={20} style={{ color: "#8A97A6" }} className="mb-1" />
                  <span className="text-xs text-white font-medium">{fileName || "Click to upload donor selfie"}</span>
                  <span className="text-[10px] text-[#5B6572]">Supports JPEG, PNG</span>
                  <input type="file" id="liveFaceFile" accept="image/*" className="hidden" onChange={handleFileChange} />
                </div>
              )}
            </div>
            
            <div className="flex gap-3">
              <button 
                onClick={handleVerify}
                disabled={!b64Image || liveLoading}
                className="flex-1 rounded-lg py-2.5 text-xs font-semibold text-black hover:opacity-90 disabled:opacity-50 cursor-pointer transition-opacity"
                style={{ background: ACCENT }}
              >
                {liveLoading ? "Processing..." : "Run Verification"}
              </button>
              
              <div className="flex-1 flex gap-2">
                <input 
                  type="text" 
                  value={enrollName} 
                  onChange={(e) => setEnrollName(e.target.value)} 
                  placeholder="Name for Enrollment"
                  className="flex-1 bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 text-xs text-white outline-none focus:border-[#2fd9c4] transition-colors"
                />
                <button 
                  onClick={handleEnroll}
                  disabled={!b64Image || !enrollName || liveLoading}
                  className="rounded-lg px-4 py-2.5 text-xs font-semibold text-white border border-[rgba(255,255,255,0.15)] hover:bg-[rgba(255,255,255,0.05)] disabled:opacity-50 cursor-pointer transition-colors"
                >
                  Enroll
                </button>
              </div>
            </div>
          </div>
          
          <div className="bg-[#05070a] border border-[rgba(255,255,255,0.05)] rounded-xl p-4 flex flex-col justify-center min-h-[160px] shadow-inner relative overflow-hidden">
            {liveLoading && (
              <div className="text-center space-y-2">
                <div className="h-6 w-6 border-2 border-t-transparent border-[#2fd9c4] rounded-full animate-spin mx-auto" />
                <span className="block text-[11px] text-[#8A97A6] font-mono animate-pulse">Extracting SFace identity descriptors...</span>
              </div>
            )}
            {!liveLoading && !liveResult && !liveError && !enrollStatus && (
              <div className="text-center space-y-1">
                <ShieldCheck size={22} className="mx-auto" style={{ color: "#5b6572" }} />
                <span className="block text-[11px] text-[#5B6572] font-mono">Biometric scanner ready. Select photo source to begin analysis.</span>
              </div>
            )}
            {enrollStatus && (
              <div className="space-y-2 text-center">
                <CheckCircle size={22} className="mx-auto text-teal-400" />
                <span className="block text-xs font-semibold text-teal-400">ENROLLMENT COMPLETE</span>
                <p className="text-[11px] text-[#8A97A6] font-mono">{enrollStatus}</p>
              </div>
            )}
            {liveError && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <XCircle size={16} style={{ color: STATE.breach.dot }} />
                  <span className="text-xs font-semibold" style={{ color: STATE.breach.text }}>DETECTION FAILED</span>
                </div>
                <p className="text-xs text-white leading-normal font-mono">{liveError}</p>
              </div>
            )}
            {liveResult && (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  {liveResult.duplicate_detected ? (
                    <>
                      <XCircle size={16} style={{ color: STATE.breach.dot }} />
                      <span className="text-xs font-bold tracking-wider" style={{ color: STATE.breach.text }}>LOCKOUT ALERT: DUPLICATE FOUND</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle size={16} style={{ color: STATE.safe.dot }} />
                      <span className="text-xs font-bold tracking-wider" style={{ color: STATE.safe.text }}>VERIFICATION CLEAR: SAFE</span>
                    </>
                  )}
                </div>
                
                <div className="rounded-lg bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.04)] p-3 space-y-1.5">
                  <p className="text-xs text-white leading-relaxed">{liveResult.message}</p>
                  {liveResult.duplicate_detected && (
                    <div className="pt-1.5 border-t border-[rgba(255,255,255,0.04)] flex flex-wrap gap-x-4 gap-y-1 text-[10px] text-[#8A97A6]">
                      <div>Match Confidence: <span className="font-mono font-bold text-white">{liveResult.confidence}%</span></div>
                      <div>Conflict ID: <span className="font-mono text-white">{liveResult.matched_donor?.id || "N/A"}</span></div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </Glass>

      {/* Verification / Lockout Queue */}
      <Glass className="p-5 animate-none">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3 animate-none">
          <div>
            <h2 className="text-sm font-semibold text-white">Active Lockout Database</h2>
            <p className="text-[10px] text-[#5B6572] mt-0.5">List of verified donors currently locked out from donation for the mandatory 56-day window.</p>
          </div>
          
          <div className="flex items-center gap-3 animate-none">
            <span className="rounded-full border px-2.5 py-1 text-[10px] border-solid border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)] text-[#8A97A6]">
              Clinical limit: {LOCKOUT_DAYS ?? 56} Days
            </span>
            <div className="flex items-center gap-2 rounded-lg border px-2.5 py-1.5 text-xs border-solid" style={{ borderColor: "rgba(255,255,255,0.08)", color: "#8A97A6", background: "rgba(255,255,255,0.01)" }}>
              <Search size={12} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search database..."
                className="w-32 bg-transparent text-white outline-none placeholder:text-[#5B6572] border-none text-[11px]"
              />
            </div>
          </div>
        </div>

        {donorsLoading ? (
          <div className="text-center py-10">
            <div className="h-5 w-5 border-2 border-t-transparent border-[#8A97A6] rounded-full animate-spin mx-auto mb-2" />
            <span className="text-xs text-[#8A97A6] font-mono">Syncing database entries...</span>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 py-12 text-center animate-none rounded-xl border border-dashed border-[rgba(255,255,255,0.04)] bg-[rgba(255,255,255,0.005)]">
            <SearchX size={24} style={{ color: "#5B6572" }} />
            <p className="text-xs font-semibold text-white">No Lockout Records Found</p>
            <p className="text-[10px] text-[#5B6572] max-w-sm leading-normal">
              {query ? "Try checking spelling or clear search parameters." : "Lockout database is empty. Register the first donor selfie above to establish the biometric lockout telemetry."}
            </p>
          </div>
        ) : (
          <div className="space-y-2.5 animate-none">
            {filtered.map((d) => {
              return (
                <div key={d.id} className="flex items-center justify-between rounded-xl border p-3 border-solid bg-[rgba(255,255,255,0.01)] hover:bg-[rgba(255,255,255,0.02)] transition-colors" style={{ borderColor: "rgba(255,255,255,0.05)" }}>
                  <div className="flex items-center gap-3 animate-none">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[rgba(47,217,196,0.05)] border border-[rgba(47,217,196,0.15)] shadow-inner">
                      <User size={13} style={{ color: "#2fd9c4" }} />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">{d.name}</p>
                      <div className="flex items-center gap-3 text-[10px] text-[#8A97A6] mt-0.5 font-mono">
                        <div>ID: <span className="text-[#C7D0DA] font-bold">#{d.id}</span></div>
                        <div className="flex items-center gap-1"><Calendar size={10} /> {new Date(d.enrolled_at).toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 rounded-full border border-[rgba(248,113,113,0.15)] bg-[rgba(248,113,113,0.05)] px-3 py-1 text-[10px] font-bold text-[#f87171]">
                    <ShieldAlert size={11} /> LOCKOUT ACTIVE
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Glass>
    </div>
  );
}
