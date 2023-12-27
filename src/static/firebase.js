import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";

import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-analytics.js";
const { initializeAppCheck, ReCaptchaV3Provider } = require("firebase/app-check");

// TODO: Add SDKs for Firebase products that you want to use

// https://firebase.google.com/docs/web/setup#available-libraries


// Your web app's Firebase configuration

const firebaseConfig = {

    apiKey: "AIzaSyCG1x8rp4PCl71jZRMb24K2GB-jhzUlg2I",

    authDomain: "memenetted.firebaseapp.com",

    projectId: "memenetted",

    storageBucket: "memenetted.appspot.com",

    messagingSenderId: "1084077420683",

    appId: "1:1084077420683:web:224d6570d23e249218a48e",

    measurementId: "G-PYPP5TXMN8"

};

const appCheck = initializeAppCheck(app, {
    provider: new ReCaptchaV3Provider('abcdefghijklmnopqrstuvwxy-1234567890abcd'),

    // Optional argument. If true, the SDK automatically refreshes App Check
    // tokens as needed.
    isTokenAutoRefreshEnabled: true
});
// Initialize Firebase

const app = initializeApp(firebaseConfig);

const analytics = getAnalytics(app);
