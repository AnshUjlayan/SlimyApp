import React, { useState } from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import api from "../../Config/apiConfig";

const GoogleAuth = () => {
  const [user, setUser] = useState(null);
  // const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;
  const GOOGLE_CLIENT_ID =
    "492813304799-ukoph11jr2b8hminsttti3nerl5ul721.apps.googleusercontent.com";

  const handleLoginSuccess = (response) => {
    const { credential } = response; // Get the credential from Google's response
    api
      .post("http://localhost:8000/api/google-login/", {
        tokenId: credential,
      })
      .then((res) => {
        // Store the tokens and set user state
        localStorage.setItem("access_token", res.data.access);
        localStorage.setItem("refresh_token", res.data.refresh);
        setUser({
          email: response.profileObj.email,
          name: response.profileObj.name,
          imageUrl: response.profileObj.imageUrl,
        });
        console.log("Login success: ", res.data);
      })
      .catch((err) => {
        console.error("Login failed: ", err);
      });
  };

  const handleLoginFailure = (error) => {
    console.error("Login failed: ", error);
  };

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <div>
        <h2>Login with Google</h2>
        <GoogleLogin
          onSuccess={handleLoginSuccess}
          onFailure={handleLoginFailure}
        />
        {user && (
          <div>
            <h3>Welcome, {user.name}</h3>
            <img src={user.imageUrl} alt="Profile" />
          </div>
        )}
      </div>
    </GoogleOAuthProvider>
  );
};

export default GoogleAuth;