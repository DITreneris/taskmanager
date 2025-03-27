import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import brain from "brain";
import { Button } from "components/Button";

export default function GmailCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get query parameters from URL
        const searchParams = new URLSearchParams(location.search);
        const code = searchParams.get("code");
        const state = searchParams.get("state");

        if (!code || !state) {
          setStatus("error");
          setError("Invalid callback URL: missing required parameters");
          return;
        }

        // Current URL as the redirect URI (same as the one used for login)
        const redirectUri = `${window.location.origin}${window.location.pathname}`;

        // Call the callback endpoint
        await brain.callback({
          code, 
          state, 
          redirect_uri: redirectUri
        });

        // Successfully authenticated
        setStatus("success");

        // Automatically redirect after short delay
        setTimeout(() => {
          navigate("/gmail-auth");
        }, 2000);
      } catch (err) {
        console.error("Authentication callback error:", err);
        setStatus("error");
        setError("Failed to complete authentication");
      }
    };

    handleCallback();
  }, [location, navigate]);

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-4">Gmail Authentication</h2>
          
          {status === "loading" && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mb-4"></div>
              <p>Completing authentication...</p>
            </div>
          )}
          
          {status === "success" && (
            <div className="text-center py-8">
              <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-green-100 text-green-500 mb-4">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2">Authentication Successful!</h3>
              <p className="text-gray-600 mb-4">Your Gmail account has been connected successfully.</p>
              <p className="text-sm text-gray-500">Redirecting you back...</p>
            </div>
          )}
          
          {status === "error" && (
            <div className="text-center py-8">
              <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-red-100 text-red-500 mb-4">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2">Authentication Failed</h3>
              <p className="text-gray-600 mb-4">{error || "There was an error connecting your Gmail account."}</p>
              <Button onClick={() => navigate("/gmail-auth")} className="mt-2">
                Try Again
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
