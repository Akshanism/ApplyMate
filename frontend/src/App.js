import { useState } from "react";
import "@/App.css";
import { UploadCloud, FileText, Sparkles, Copy, Download, Check } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [copiedSection, setCopiedSection] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const extension = file.name.split('.').pop().toLowerCase();
      if (extension === 'pdf' || extension === 'docx') {
        setResumeFile(file);
        setError("");
      } else {
        setError("Please upload a PDF or DOCX file");
        setResumeFile(null);
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      const extension = file.name.split('.').pop().toLowerCase();
      if (extension === 'pdf' || extension === 'docx') {
        setResumeFile(file);
        setError("");
      } else {
        setError("Please upload a PDF or DOCX file");
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleSubmit = async () => {
    if (!resumeFile) {
      setError("Please upload your resume");
      return;
    }
    if (!jobDescription.trim()) {
      setError("Please paste the job description");
      return;
    }

    setLoading(true);
    setError("");
    setResults(null);

    try {
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('job_description', jobDescription);

      const response = await axios.post(`${API}/tailor-application`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text, section) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(""), 2000);
  };

  const handleDownload = (text, filename) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-opal-bg">
      {/* Subtle glow gradient at top */}
      <div className="fixed top-0 left-0 right-0 h-96 bg-glow-gradient pointer-events-none" />
      
      <div className="relative max-w-2xl mx-auto px-6 py-12 md:py-20 min-h-screen flex flex-col">
        {/* Hero Section */}
        <div className="text-center relative z-10 mb-16">
          <h1 className="text-4xl md:text-5xl font-heading font-semibold tracking-tight text-slate-50 mb-4">
            ApplyMate
          </h1>
          <p className="text-base md:text-lg text-slate-400 max-w-xl mx-auto leading-relaxed">
            Your AI-powered copilot for professional job applications
          </p>
        </div>

        {/* Main Form */}
        <div className="space-y-8 relative z-10">
          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-3">
              Resume
            </label>
            <div
              data-testid="file-upload-zone"
              className="file-upload-zone border-2 border-dashed border-white/10 hover:border-opal-primary/50 hover:bg-white/5 rounded-2xl p-10 text-center cursor-pointer group"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => document.getElementById('file-input').click()}
            >
              <input
                id="file-input"
                data-testid="file-input"
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="flex flex-col items-center space-y-3">
                {resumeFile ? (
                  <FileText className="w-12 h-12 text-opal-primary" />
                ) : (
                  <UploadCloud className="w-12 h-12 text-slate-500 group-hover:text-opal-primary transition-colors duration-300" />
                )}
                <div>
                  <p className="text-slate-300 font-medium">
                    {resumeFile ? resumeFile.name : "Drop your resume here"}
                  </p>
                  <p className="text-sm text-slate-500 mt-1">
                    {resumeFile ? "Click to change" : "PDF or DOCX, max 10MB"}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Job Description */}
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-3">
              Job Description
            </label>
            <textarea
              data-testid="job-description-input"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the complete job description here..."
              className="w-full bg-white/5 border border-white/10 focus:border-opal-primary/50 focus:ring-1 focus:ring-opal-primary/50 rounded-xl p-6 text-base text-slate-200 placeholder:text-slate-600 resize-y min-h-[200px] outline-none transition-all duration-300"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div data-testid="error-message" className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Generate Button */}
          <button
            data-testid="generate-button"
            onClick={handleSubmit}
            disabled={loading}
            className="generate-btn w-full py-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white font-semibold text-lg shadow-neon transition-all duration-300 flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-pulse-soft">
                  <Sparkles className="w-5 h-5" />
                </div>
                <span>Tailoring your application...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Tailor Application</span>
              </>
            )}
          </button>
        </div>

        {/* Results Section */}
        {results && (
          <div data-testid="results-section" className="mt-12 results-fade-in">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
              <h2 className="text-2xl md:text-3xl font-heading font-medium tracking-tight text-white/90 mb-6">
                Your Tailored Application
              </h2>
              
              <Tabs defaultValue="resume" className="w-full">
                <TabsList className="bg-white/5 p-1 rounded-lg w-full grid grid-cols-3 mb-6">
                  <TabsTrigger 
                    data-testid="tab-resume"
                    value="resume" 
                    className="data-[state=active]:bg-white/10 data-[state=active]:text-white text-slate-400 rounded-md py-2"
                  >
                    Resume
                  </TabsTrigger>
                  <TabsTrigger 
                    data-testid="tab-cover-letter"
                    value="cover" 
                    className="data-[state=active]:bg-white/10 data-[state=active]:text-white text-slate-400 rounded-md py-2"
                  >
                    Cover Letter
                  </TabsTrigger>
                  <TabsTrigger 
                    data-testid="tab-email"
                    value="email" 
                    className="data-[state=active]:bg-white/10 data-[state=active]:text-white text-slate-400 rounded-md py-2"
                  >
                    Email
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="resume" className="space-y-4">
                  <div className="space-y-3">
                    {results.resume_bullets.map((bullet, idx) => (
                      <div key={idx} className="flex items-start space-x-3 text-slate-300">
                        <span className="text-opal-primary mt-1">•</span>
                        <p className="flex-1 leading-relaxed">{bullet}</p>
                      </div>
                    ))}
                  </div>
                  <div className="flex space-x-3 pt-4">
                    <button
                      data-testid="copy-resume-button"
                      onClick={() => handleCopy(results.resume_bullets.join('\n• '), 'resume')}
                      className="flex items-center space-x-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-slate-300 transition-all duration-300"
                    >
                      {copiedSection === 'resume' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      <span>{copiedSection === 'resume' ? 'Copied!' : 'Copy'}</span>
                    </button>
                    <button
                      data-testid="download-resume-button"
                      onClick={() => handleDownload('• ' + results.resume_bullets.join('\n• '), 'resume_bullets.txt')}
                      className="flex items-center space-x-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-slate-300 transition-all duration-300"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download</span>
                    </button>
                  </div>
                </TabsContent>

                <TabsContent value="cover" className="space-y-4">
                  <div className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {results.cover_letter}
                  </div>
                  <div className="flex space-x-3 pt-4">
                    <button
                      data-testid="copy-cover-letter-button"
                      onClick={() => handleCopy(results.cover_letter, 'cover')}
                      className="flex items-center space-x-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-slate-300 transition-all duration-300"
                    >
                      {copiedSection === 'cover' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      <span>{copiedSection === 'cover' ? 'Copied!' : 'Copy'}</span>
                    </button>
                    <button
                      data-testid="download-cover-letter-button"
                      onClick={() => handleDownload(results.cover_letter, 'cover_letter.txt')}
                      className="flex items-center space-x-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-slate-300 transition-all duration-300"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download</span>
                    </button>
                  </div>
                </TabsContent>

                <TabsContent value="email" className="space-y-4">
                  <div className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {results.application_email}
                  </div>
                  <div className="flex space-x-3 pt-4">
                    <button
                      data-testid="copy-email-button"
                      onClick={() => handleCopy(results.application_email, 'email')}
                      className="flex items-center space-x-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-slate-300 transition-all duration-300"
                    >
                      {copiedSection === 'email' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      <span>{copiedSection === 'email' ? 'Copied!' : 'Copy'}</span>
                    </button>
                    <button
                      data-testid="download-email-button"
                      onClick={() => handleDownload(results.application_email, 'application_email.txt')}
                      className="flex items-center space-x-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-slate-300 transition-all duration-300"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download</span>
                    </button>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;