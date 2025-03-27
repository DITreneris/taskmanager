import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import brain from "brain";
import { Button } from "components/Button";
import { AuthStatus, UserProfile } from "types";

export default function GmailAuth() {
  const navigate = useNavigate();
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkAuthStatus = async () => {
    try {
      setLoading(true);
      const response = await brain.auth_status();
      const data: AuthStatus = await response.json();
      setAuthStatus(data);

      if (data.is_authenticated) {
        try {
          const profileResponse = await brain.get_user_profile();
          const profileData: UserProfile = await profileResponse.json();
          setProfile(profileData);
        } catch (err) {
          console.error("Error fetching user profile:", err);
        }
      }
    } catch (err) {
      console.error("Error checking auth status:", err);
      setError("Failed to check authentication status");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const handleLogin = async () => {
    try {
      setError(null);
      setLoading(true);
      
      // Get the current URL for the redirect
      const redirectUri = `${window.location.origin}/gmail-callback`;
      
      const response = await brain.login({ redirect_uri: redirectUri });
      const data = await response.json();
      
      if (data.auth_url) {
        // Redirect to Google's OAuth consent screen
        window.location.href = data.auth_url;
      } else {
        setError("Authentication failed: No auth URL received");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      setLoading(true);
      await brain.logout();
      setAuthStatus({ is_authenticated: false });
      setProfile(null);
    } catch (err) {
      console.error("Logout error:", err);
      setError("Logout failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-4">Gmail Connection</h2>
          
          {loading ? (
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : error ? (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
              <Button onClick={checkAuthStatus} className="mt-2 w-full">
                Try Again
              </Button>
            </div>
          ) : authStatus?.is_authenticated ? (
            <div>
              <div className="flex items-center mb-4">
                {profile?.picture && (
                  <img 
                    src={profile.picture} 
                    alt={profile.name} 
                    className="h-12 w-12 rounded-full mr-4"
                  />
                )}
                <div>
                  <p className="font-medium">{profile?.name || authStatus.username}</p>
                  <p className="text-gray-600 text-sm">{profile?.email || authStatus.email}</p>
                </div>
              </div>
              
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                Connected to Gmail successfully!
              </div>
              
              <div className="space-y-3">
                <Button
                  onClick={() => navigate("/emails")}
                  className="w-full bg-blue-600 hover:bg-blue-700 focus:ring-blue-500"
                >
                  View Scanned Emails
                </Button>
                
                <Button 
                  onClick={handleLogout}
                  variant="outline"
                  className="w-full"
                >
                  Disconnect Gmail
                </Button>
              </div>
            </div>
          ) : (
            <div>
              <p className="mb-4 text-gray-600">
                Connect your Gmail account to scan for meeting requests and automate your scheduling.
              </p>
              
              <Button 
                onClick={handleLogin} 
                className="w-full mb-4"
              >
                Connect Gmail Account
              </Button>
              
              <p className="text-xs text-gray-500">
                Note: Tempo will only read your emails to detect meeting requests and will not store 
                the full content of your emails. You can disconnect access at any time.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
