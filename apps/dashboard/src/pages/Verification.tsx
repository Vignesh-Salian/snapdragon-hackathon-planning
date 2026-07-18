import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { Search, SearchX, User, ShieldAlert, Camera, CheckCircle, XCircle } from "lucide-react";
import { STATE, CONFIDENCE_THRESHOLD, ACCENT, type DonorVerifyResponse } from "../types";
import { verificationQueue } from "../mocks/data";
import { verifyDonor, enrollDonor } from "../services/api";
import Glass from "../components/Glass";
import StatePill from "../components/StatePill";

export interface VerificationPageProps {
  openAlert?: () => void;
}

/**
 * Donor Verification page component showing the registration queues, match confidence levels,
 * and duplicate alert lockout reviews.
 */
export default function Verification({ openAlert }: VerificationPageProps) {
  const context = useOutletContext<{ openAlert: () => void }>();
  const activeOpenAlert = openAlert || context?.openAlert;

  const [query, setQuery] = useState("");
  const [enrollName, setEnrollName] = useState("");
  const [b64Image, setB64Image] = useState("");
  const [fileName, setFileName] = useState("");
  const [liveLoading, setLiveLoading] = useState(false);
  const [liveResult, setLiveResult] = useState<DonorVerifyResponse | null>(null);
  const [enrollStatus, setEnrollStatus] = useState<string | null>(null);

  const filtered = verificationQueue.filter((v) =>
    v.response.matched_donor.name.toLowerCase().includes(query.toLowerCase())
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setLiveResult(null);
    setEnrollStatus(null);
    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result as string;
      setB64Image(result.split(",")[1]); // Extract base64 part
    };
    reader.readAsDataURL(file);
  };

  const handleVerify = async () => {
    if (!b64Image) return;
    setLiveLoading(true);
    setLiveResult(null);
    try {
      const res = await verifyDonor(b64Image);
      setLiveResult(res);
    } catch (err: any) {
      console.error(err);
      setLiveResult({
        duplicate_detected: false,
        confidence: 0,
        matched_donor: { id: 0, name: "", enrolled_at: "" },
        message: `API Error: ${err.message || "Failed to reach gateway"}`
      });
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
      setEnrollStatus(`Success! Enrolled with ID: ${res.id}`);
      // Clear inputs
      setEnrollName("");
      setFileName("");
      setB64Image("");
    } catch (err: any) {
      console.error(err);
      setEnrollStatus(`Enrollment Error: ${err.message || "Failed to reach gateway"}`);
    } finally {
      setLiveLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6 animate-none">
      {/* Live Biometric Test Desk */}
      <Glass className="p-5 animate-none">
        <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
          <Camera size={15} style={{ color: ACCENT }} /> Live Biometric Verification Desk
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="mb-4">
              <label className="mb-1.5 block text-xs" style={{ color: "#8A97A6" }}>Select Donor Photo</label>
              <div 
                onClick={() => document.getElementById("liveFaceFile")?.click()}
                className="border-2 border-dashed border-[rgba(255,255,255,0.08)] hover:border-[#2fd9c4] rounded-lg p-6 text-center cursor-pointer transition-colors"
              >
                <span className="text-xs text-white">{fileName || "Click to upload donor selfie"}</span>
                <input type="file" id="liveFaceFile" accept="image/*" className="hidden" onChange={handleFileChange} />
              </div>
            </div>
            
            <div className="flex gap-3">
              <button 
                onClick={handleVerify}
                disabled={!b64Image || liveLoading}
                className="flex-1 rounded-lg py-2.5 text-xs font-semibold text-black hover:opacity-90 disabled:opacity-50 cursor-pointer"
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
                  className="flex-1 bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] rounded-lg px-2 text-xs text-white outline-none"
                />
                <button 
                  onClick={handleEnroll}
                  disabled={!b64Image || !enrollName || liveLoading}
                  className="rounded-lg px-3 py-2.5 text-xs font-semibold text-white border border-[rgba(255,255,255,0.15)] hover:bg-[rgba(255,255,255,0.05)] disabled:opacity-50 cursor-pointer"
                >
                  Enroll
                </button>
              </div>
            </div>
          </div>
          
          <div className="bg-[#06080c] border border-[rgba(255,255,255,0.08)] rounded-xl p-4 flex flex-col justify-center min-h-[120px]">
            {liveLoading && <span className="text-xs animate-pulse" style={{ color: '#8A97A6' }}>Analyzing face landmarks and identity embeddings...</span>}
            {!liveLoading && !liveResult && !enrollStatus && <span className="text-xs text-[#5B6572] font-mono">Select a file and click "Run Verification" or type a name to "Enroll".</span>}
            {enrollStatus && <span className="text-xs text-[#57ffc9] font-mono">{enrollStatus}</span>}
            {liveResult && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  {liveResult.duplicate_detected ? (
                    <>
                      <XCircle size={16} style={{ color: STATE.breach.dot }} />
                      <span className="text-xs font-semibold" style={{ color: STATE.breach.text }}>LOCKOUT ALERT: DUPLICATE DETECTED</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle size={16} style={{ color: STATE.safe.dot }} />
                      <span className="text-xs font-semibold" style={{ color: STATE.safe.text }}>VERIFICATION CLEAR: NEW DONOR</span>
                    </>
                  )}
                </div>
                <p className="text-xs text-white leading-normal">{liveResult.message}</p>
                {liveResult.duplicate_detected && (
                  <div className="text-[10px]" style={{ color: "#8A97A6" }}>
                    Confidence Match: <span className="font-mono text-white">{liveResult.confidence}%</span> | 
                    Matched ID: <span className="font-mono text-white">{liveResult.matched_donor?.id || "N/A"}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </Glass>

      <Glass className="p-5 animate-none">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2 animate-none">
          <h2 className="text-sm font-semibold text-white">Verification Queue</h2>
          <div className="flex items-center gap-2 animate-none">
            <span
              className="rounded-full border px-2.5 py-1 text-[11px] border-solid"
              style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}
              title="Matches above this confidence are auto-flagged as potential duplicates"
            >
              Flag threshold: {CONFIDENCE_THRESHOLD}%
            </span>
            <div className="flex items-center gap-2 rounded-lg border px-2.5 py-1.5 text-xs border-solid" style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}>
              <Search size={12} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search donor"
                className="w-28 bg-transparent text-white outline-none placeholder:text-[#5B6572] border-none"
              />
            </div>
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center animate-none">
            <SearchX size={22} style={{ color: "#5B6572" }} />
            <p className="text-sm text-white">No matching donor found</p>
            <p className="text-[11px]" style={{ color: "#5B6572" }}>Check the spelling, or clear the search to see the full queue.</p>
          </div>
        ) : (
          <div className="space-y-2 animate-none">
            {filtered.map((v) => {
              const s = STATE[v.state];
              const { confidence, matched_donor } = v.response;
              const overThreshold = confidence >= CONFIDENCE_THRESHOLD;
              return (
                <div key={matched_donor.name} className="flex items-center justify-between rounded-lg border p-3 border-solid" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
                  <div className="flex items-center gap-3 animate-none">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full" style={{ background: s.bg }}>
                      <User size={14} style={{ color: s.text }} />
                    </div>
                    <div>
                      <p className="text-sm text-white">{matched_donor.name}</p>
                      <p className="text-[11px]" style={{ color: overThreshold ? s.text : "#5B6572" }}>
                        Confidence match: {confidence}%{overThreshold ? ` — above ${CONFIDENCE_THRESHOLD}% threshold` : ""}
                      </p>
                    </div>
                  </div>
                  {v.state === "breach" ? (
                    <button onClick={activeOpenAlert} className="flex items-center gap-1 rounded-lg border px-3 py-1.5 text-xs font-medium cursor-pointer border-solid" style={{ borderColor: s.border, color: s.text }}>
                      <ShieldAlert size={12} /> Review lockout
                    </button>
                  ) : (
                    <StatePill state={v.state} />
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Glass>
    </div>
  );
}
