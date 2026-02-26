const COGNITO_DOMAIN = "https://ap-southeast-1augeyqeun.auth.ap-southeast-1.amazoncognito.com";
const CLIENT_ID = "ngqr5509uukbre26as02cb0ks";
const REDIRECT_URI = `${window.location.origin}/pages/index.html`;
const LOGOUT_URI = `${window.location.origin}/login`;

// Parse token from URL hash after Cognito redirect
const _params = new URLSearchParams(window.location.hash.substring(1));
const _token = _params.get("id_token");
if (_token) {
    sessionStorage.setItem("id_token", _token);
    window.history.replaceState({}, "", window.location.pathname);
}

function getToken() { return sessionStorage.getItem("id_token"); }

function getUser() {
    const token = getToken();
    if (!token) return null;
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return { username: payload["cognito:username"], email: payload.email, groups: payload["cognito:groups"] || [] };
    } catch { return null; }
}

function login() {
    window.location.href = `${COGNITO_DOMAIN}/login?client_id=${CLIENT_ID}&response_type=token&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=openid+email`;
}

function logout() {
    sessionStorage.clear();
    window.location.href = `${COGNITO_DOMAIN}/logout?client_id=${CLIENT_ID}&logout_uri=${encodeURIComponent(LOGOUT_URI)}`;
}

function requireAuth() {
    if (!getToken()) window.location.href = "/login";
}
