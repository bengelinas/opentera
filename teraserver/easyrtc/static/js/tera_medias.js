// Audio - video sources management
var videoSources = [];
var audioSources = [];
let localCapabilities = {'video2':false, 'screenControl': false, 'screenSharing': false};

// Control flags
var deviceEnumCompleted = false;

async function fillDefaultSourceList(){
    console.log("fillDefaultSourceList()");
    videoSources.length=0;
    audioSources.length=0;

    // Open a stream to ask for permissions and allow listing of full name of devices.
    try{
        /*await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: {
                width: {ideal: 1280, max: 1920 },
                height: {ideal: 720, max: 1080 },
                frameRate: {min: 15}//, ideal: 30}
            }
        });*/
        await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: true
        });
    }catch(err) {
        showError("fillDefaultSourceList() - getUserMedia",
            translator.translateForKey("errors.no-media-access", currentLang) + "<br><br>" +
            translator.translateForKey("errors.error-msg", currentLang) +
            ":<br>" + err.name + " - " + err.message, true);
        throw err;
    }

    try {
        let devices = await navigator.mediaDevices.enumerateDevices();
        devices.forEach(device => {
            if (device.kind === "videoinput"){
                if (!device.label.includes(" IR ")) // Filter "IR" camera, since they won't work.
                    videoSources[videoSources.length] = device;
            }
            if (device.kind === "audioinput"){
                audioSources[audioSources.length] = device;
            }

        });
    }catch(err) {
        showError("fillDefaultSourceList() - enumerateDevices", err.name + " - " + err.message, true);
        throw err;
    }

    deviceEnumCompleted = true;

    selectDefaultSources();

}

function removeVideoSource(video_name){
    for (let i=0; i<videoSources.length; i++){
        if (videoSources[i].label.includes(video_name)){
            console.log("Removed " + video_name + " from video source list.");
            videoSources.splice(i,1);
            return;
        }
    }
    console.log("No need to remove " + video_name + " - not in source list.");
}

function selectVideoSource(source){

    let video = JSON.parse(source);
    console.log("Selecting Video: " + video.name + ", index: " + video.index + "(" + videoSources.length + " total)");

    let found = false;

    for (let i=0; i<videoSources.length; i++){
        console.log("-- Video is " + videoSources[i].label + " ?");
        if (videoSources[i].label.includes(video.name)){
            console.log("Found source at: " + i);
            currentConfig.currentVideoSourceIndex = i;
            updateLocalAudioVideoSource(1);
            found = true;
            break;
        }
    }
    if (!found){
        if (video.index !== undefined){
            console.log("Selected by index.");
            currentConfig.currentVideoSourceIndex = video.index;
            updateLocalAudioVideoSource(1);
        }
    }
}

function selectAudioSource(source){

    let audio = JSON.parse(source);
    console.log("Selecting Audio: " + audio.name + "(" + audioSources.length + " total)");
    //console.log(audioSources);
    let found = false;
    for (let i=0; i<audioSources.length; i++){
        let name = audioSources[i].label;
        if (name === "")
            name = audioSources[i].deviceId;

        console.log("-- Audio is " + name + " ?");
        if (name.includes(audio.name)){
            console.log("Found source at: " + i);

            currentConfig.currentAudioSourceIndex = i;
            updateLocalAudioVideoSource(1);
            found = true;
            break;
        }
    }

    /*if (teraConnected && !connected && deviceEnumCompleted)
            connect();*/

    //initialSourceSelect = true;

}

function selectSecondarySources(source){
    let sources = JSON.parse(source);
    console.log("Selecting Second Sources: Video = " + sources.video + ", Audio = " + sources.audio);

    // Video
    let found = false;
    if (sources.video !== ""){
        for (let i=0; i<videoSources.length; i++){
            console.log("-- Video is " + videoSources[i].label + " ?");
            if (videoSources[i].label.includes(sources.video)){
                console.log("Found source at: " + i);
                currentConfig.currentVideoSource2Index = i;
                found = true;
                break;
            }
        }
    }

    if (!found){
        currentConfig.currentVideoSource2Index = -1;
    }

    // Audio
    found = false;
    if (sources.audio !== ""){
        for (let i=0; i<audioSources.length; i++){
            console.log("-- Audio is " + audioSources[i].label + " ?");
            if (audioSources[i].label.includes(sources.audio)){
                console.log("Found source at: " + i);
                currentConfig.currentAudioSource2Index = i;
                found = true;
                break;
            }
        }
    }

    if (!found){
        currentConfig.currentAudioSource2Index = -1;
    }

    if (sources.audio !== "" || sources.video !== ""){
        //showSecondaryLocalSourcesIcons(true, false);
        localCapabilities.video2 = true;
    }else{
        //showSecondaryLocalSourcesIcons(false, false);
        localCapabilities.video2 = false;
    }
    broadcastlocalCapabilities();
    //updateLocalAudioVideoSource(2);
}

function selectDefaultSources(){
    console.log("Selecting default sources");
    if (currentConfig.currentVideoSourceIndex === -1){
        console.log("No video specified - looking for default...");
        let found = false;
        for (let i=0; i<videoSources.length; i++){
            console.log("Video = " + videoSources[i].label + " ?");
            // TODO: Not a good way to filter front cameras... should use constraints?
            if (videoSources[i].label.toLowerCase().includes("avant") || videoSources[i].label.toLowerCase().includes("front")){
                console.log("Found source at: " + i);
                currentConfig.currentVideoSourceIndex = i;
                found = true;
                break;
            }
        }
        if (!found){
            console.log("Default not found - using first one in the list.");
            currentConfig.currentVideoSourceIndex = 0;
        }
    }

    if (currentConfig.currentAudioSourceIndex === -1){
        currentConfig.currentAudioSourceIndex = 0; // Default audio
    }
}


function setCapabilities(peerid, video2, screenControl, screenSharing){

    console.log("Setting Capabilities: " + peerid + ", video2 = " + video2 + ", control = " + screenControl +
        ", sharing = " + screenSharing);
    let cap = {'video2':video2, 'screenControl': screenControl, 'screenSharing': screenSharing};

    if (peerid === local_peerid){
        console.log(" -- Local ID - settings values.");
        localCapabilities = cap;
    }else {
        console.log(" -- Remote ID received: " + peerid + ", I am " + local_peerid);
        // Find and update capabilities in remoteContacts
        // console.log(remoteContacts);
        let index = getContactIndexForPeerId(peerid);
        if (index !== undefined) {
            remoteContacts[index].capabilities = cap;
        }
    }
}

function getActiveStreams(){
    let streams = [];

    for (let i=0; i<localStreams.length; i++){
        if (localStreams[i].stream){
            streams.push(localStreams[i].stream);
        }
    }

    for (let i=0; i<remoteStreams.length; i++){
        if (remoteStreams[i].stream){
            streams.push(remoteStreams[i].stream);
        }
    }
    return streams;

}
