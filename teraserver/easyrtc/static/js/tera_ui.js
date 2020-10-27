let localTimerHandles = [0, 0];
let remoteTimerHandles = [0, 0, 0, 0];

let localScreenSharing = false;
let localSecondSource = false;

let primaryView = {peerid: 0, streamName: 'default'};

function initUI(){
    $('#configDialog').on('hidden.bs.modal', configDialogClosed);
}

function resetInactiveTimer(local, index){
    stopInactiveTimer(local, index);

    let timerHandle = setTimeout(inactiveTimeout, 3000, local, index);
    if (local === true){
        localTimerHandles[index-1] = timerHandle;
    }else{
        remoteTimerHandles[index-1] = timerHandle;
    }
}

function stopInactiveTimer(local, index){
    let timerHandle = (local===true) ? localTimerHandles[index-1] : remoteTimerHandles[index-1];
    if (timerHandle !== 0){
        clearTimeout(timerHandle);
        (local===true) ? localTimerHandles[index-1] = 0 : remoteTimerHandles[index-1] = 0;
    }
}

function showButtons(local, show, index){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let ptzControls = $("#" + view_prefix + "PtzControls" + index);
    let srcControls = $("#" + view_prefix + "SourcesControls" + index);
    let statusControls = $("#" + view_prefix + "ViewControls" + index)
    let videoControls = $("#" + view_prefix + "VideoControls" + index);

    if (videoControls.length){
        // Must hide individual icons according to state
        let swapButton = getButtonIcon(local, index, "SwapVideo");
        let starButton = getButtonIcon(local, index, "Star");

        if (isParticipant){
            if (primaryView.peerid === 0){
                (show) ? swapButton.show() : swapButton.hide();
            }else{
                swapButton.hide();
            }
        }else{
            (show) ? swapButton.show() : swapButton.hide();
        }

        if (!isButtonActive(local, index, "Star")){
            (show) ? starButton.show() : starButton.hide();
        }else{
            starButton.show();
        }
    }

    if (ptzControls.length){
        if (show === true){
            (hasPTZControls(local, index)) ? ptzControls.show() : ptzControls.hide();
        }else{
            ptzControls.hide();
        }
    }
    if (srcControls.length){
        // Must hide individual icons according to state
        //(show === true) ? srcControls.show() : srcControls.hide();
        let screenIcon = getButtonIcon(local, index, "ShareScreen");
        let secondSourceIcon = getButtonIcon(local, index, "Show2ndVideo");

        if (screenIcon.length){
            let iconActive = isButtonActive(local, index, "ShareScreen");
            if (iconActive === true){
                screenIcon.show();
            }else{
                (show === true && !localSecondSource) ? screenIcon.show() : screenIcon.hide();
            }
        }

        if (secondSourceIcon.length){
            // Always hide if no secondary stream selected
            if (currentConfig.currentVideoSource2Index <0 && currentConfig.currentAudioSource2Index <0)
                secondSourceIcon.hide();
            else{
                let iconActive = isButtonActive(local, index, "Show2ndVideo");
                if (iconActive === true){
                    secondSourceIcon.show();
                }else{
                    (show === true && !localScreenSharing) ? secondSourceIcon.show() : secondSourceIcon.hide();
                }
            }
        }
    }
    if (statusControls.length){
        // Must hide individual icons according to state
        let micIcon = getStatusIcon(local, index, "Mic");
        let videoIcon = getStatusIcon(local, index, "Video");
        let configIcon = $("#" + view_prefix + "Config" + index);
        let speakerIcon = getStatusIcon(local, index, "Speaker");

        if (micIcon.length){
            let iconActive = isStatusIconActive(local, index, "Mic");
            if (iconActive === true){
                (show === true) ? micIcon.show() : micIcon.hide();
            }else{
                micIcon.show();
            }
        }

        if (videoIcon.length){
            let iconActive = isStatusIconActive(local, index, "Video");
            if (iconActive === true){
                (show === true) ? videoIcon.show() : videoIcon.hide();
            }else{
                videoIcon.show();
            }
        }

        if (speakerIcon.length){
            let iconActive = isStatusIconActive(local, index, "Speaker");
            if (iconActive === true){
                (show === true) ? speakerIcon.show() : speakerIcon.hide();
            }else{
                speakerIcon.show();
            }
        }
        if (configIcon.length){
            (show === true) ? configIcon.show() : configIcon.hide();
        }
    }

}

function showStatusControls(local, index, show){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let statusControls = $("#" + view_prefix + "ViewControls" + index);
    (show === true) ? statusControls.show() : statusControls.hide();
}

function inactiveTimeout(local, index){
    stopInactiveTimer(local, index);
    showButtons(local, false, index);
}

function showAllButtons(show){
    showButtons(true, show, 1);
    showButtons(true, show, 2);
    showButtons(false, show, 1);
    showButtons(false, show, 2);
    showButtons(false, show,3);
    showButtons(false, show,4);
}

/*function showSecondaryLocalSourcesIcons(show_add_button, show_remove_button){
    (show_add_button) ? showElement('imgAddLocalVideo2') : hideElement('imgAddLocalVideo2');
    (show_remove_button) ? showElement('imgRemoveLocalVideo2') : hideElement('imgRemoveLocalVideo2');
}*/

function showVideoMirror(local, index, mirror){
    let video_widget = getVideoWidget(local, index);
    if (video_widget !== undefined){
        (mirror === true) ? video_widget.addClass('videoMirror') : video_widget.removeClass('videoMirror');
    }
}

function hideElement(id){
    $("#"+id).hide();
}

function showElement(id){
    $("#"+id).show();
}

function getStatusIcon(local, index, prefix){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    return $("#" + view_prefix + prefix + "Status" + index);
}

function getVideoWidget(local, index){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    return $("#" + view_prefix + "Video" + index);
}

function isStatusIconActive(local, index, prefix){
    let icon = getStatusIcon(local, index, prefix);
    return !icon.attr('src').includes("off");
}

function isIconActive(icon_id){
    let icon = $("#" + icon_id);
    return !icon.attr('src').includes("off");
}

function setIconState(icon_id, prefix, state){
    let icon = $("#" + icon_id);

    if (icon.length === 0)
        return;

    let iconImgPath = icon.attr('src').split('/')

    if (state === true){
        iconImgPath[iconImgPath.length-1] = prefix.toLowerCase() + ".png";
    }else{
        iconImgPath[iconImgPath.length-1] = prefix.toLowerCase() + "_off.png";
    }
    icon.attr('src', pathJoin(iconImgPath))
}

function updateStatusIconState(status, local, index, prefix){
    let icon = getStatusIcon(local, index, prefix);

    if (icon.length === 0)
        return;

    let iconImgPath = icon.attr('src').split('/')

    if (status === true){
        iconImgPath[iconImgPath.length-1] = prefix.toLowerCase() + ".png";
        let must_show = false;
        if (local){
            if (localTimerHandles[index-1] !== 0) must_show = true;
        }else{
            if (!isParticipant)
                if (remoteTimerHandles[index-1] !== 0) must_show = true;
        }
        (!must_show) ? icon.hide() : icon.show();
    }else{
        iconImgPath[iconImgPath.length-1] = prefix.toLowerCase() + "_off.png";
        icon.show();
    }
    icon.attr('src', pathJoin(iconImgPath))
}

function getButtonIcon(local, index, prefix){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    return $("#" + view_prefix + "Btn" + prefix + index);
}

function isButtonActive(local, index, prefix){
    let icon = getButtonIcon(local, index, prefix);
    if (icon !== undefined  && icon.length)
        return icon.attr('src').includes("on");
    return false;
}

function updateButtonIconState(status, local, index, prefix){
    let icon = getButtonIcon(local, index, prefix);

    if (icon !== undefined){
        if (icon.attr('src')){
            let iconImgPath = icon.attr('src').split('/')

            if (status === true){
                iconImgPath[iconImgPath.length-1] = prefix.toLowerCase() + "_on.png";
                let must_show = false;
                if (local){
                    if (localTimerHandles[index-1] !== 0) must_show = true;
                }else{
                    if (remoteTimerHandles[index-1] !== 0) must_show = true;
                }
                (!must_show) ? icon.hide() : icon.show();
            }else{
                iconImgPath[iconImgPath.length-1] = prefix.toLowerCase() + ".png";
                //icon.show();
            }
            icon.attr('src', pathJoin(iconImgPath))
        }
    }
}

function enlargeView(local, index){

    let view_id = getVideoViewId(local, index);
    let already_large = (view_id === currentLargeViewId);

    if (typeof(setCurrentUserLayout) !== "undefined"){
        if (already_large){
            // Minimize the current large view
            // Ensure we have the right layout
            setCurrentUserLayout(layouts.GRID, false);
        }else{
            // Maximize the selected view
            setCurrentUserLayout(layouts.LARGEVIEW, false, view_id);
        }
    }else{
        setLargeView(view_id);
    }


    // Update layouts
    updateUserRemoteViewsLayout(remoteStreams.length);
    updateUserLocalViewLayout(localStreams.length, remoteStreams.length);

}

function btnShareScreenClicked(){
    if (localSecondSource === true){
        console.warn("Trying to share screen while already having a second video source");
        return;
    }

    if (remoteStreams.length >= 4){
        showError("btnShareScreenClicked", "Impossible de partager l'écran: trop de sources dans la séance", true, false);
        return;
    }

    localScreenSharing = !localScreenSharing;

    // Do the screen sharing
    shareScreen(true, localScreenSharing).then(function (){

        updateButtonIconState(localScreenSharing, true, 1, "ShareScreen");

        // Show / Hide share screen button
        let btn = getButtonIcon(true, 1, "ShareScreen");
        if (localScreenSharing)
            btn.show();

        // Show / Hide second source button
        btn = getButtonIcon(true, 1, "Show2ndVideo");
        (localScreenSharing) ? btn.hide() : btn.show();

        // Show / hide mic-video-speaker icons
        showStatusControls(true, 2, !localScreenSharing);

        // Force views on new screen share
        if (!isParticipant){
            setPrimaryView(local_peerid, "ScreenShare");
            setPrimaryViewIcon(local_peerid, "ScreenShare");
        }

    }).catch(function (){
        // Revert state
        localScreenSharing = !localScreenSharing;
    });

}

function btnShow2ndLocalVideoClicked(){
    if (localScreenSharing === true){
        console.warn("Trying to add second source while already having a screen sharing source");
        return;
    }

    if (remoteStreams.length >= 4){
        showError("btnShow2ndLocalVideoClicked", "Impossible d'ajouter une deuxième source vidéo: trop de sources dans la séance.'", true, false);
        return;
    }

    localSecondSource = ! localSecondSource;

    share2ndStream(true, localSecondSource);

    updateButtonIconState(localSecondSource, true, 1, "Show2ndVideo");

    // Show / Hide screen sharing button
    let btn = getButtonIcon(true, 1, "ShareScreen");
    (localSecondSource) ? btn.hide() : btn.show();
}

function showError(err_context, err_msg, ui_display, show_retry=true){
    console.error(err_context + ": " + err_msg);

    if (ui_display === true){
        $('#errorDialogText')[0].innerHTML = err_msg;
        $('#errorDialog').modal('show');
        (show_retry) ? $('#errorRefresh').show() : $('#errorRefresh').hide();
    }
}

function showStatusMsg(status_msg){
    $('#statusLabel')[0].innerHTML = status_msg;
    $('#statusAlert').show();
}

function clearStatusMsg(){
    $('#statusAlert').hide();
}

function setConfigDialogValues(audios, videos, config){
    // Main video source selector
    let videoSelect = $('#videoSelect')[0];
    videoSelect.options.length = 0;

    // Main audio source selector
    let audioSelect = $('#audioSelect')[0];
    audioSelect.options.length = 0;

    // Secondary video source selector
    let videoSelect2 = $('#videoSelect2')[0];
    videoSelect2.options.length = 0;
    videoSelect2.options[videoSelect2.options.length] = new Option("Aucune", "0");

    // Secondary audio source selector
    let audioSelect2 = $('#audioSelect2')[0];
    audioSelect2.options.length = 0;
    audioSelect2.options[audioSelect2.options.length] = new Option("Aucune", "0");

    // Mirror toggle
    let mirrorCheck = $('#mirrorCheck')[0];
    mirrorCheck.checked = config['video1Mirror'];

    // Fill lists
    audios.forEach(audio => {
        let name = audio.label;
        if (name === "") name = audio.deviceId;
        audioSelect.options[audioSelect.options.length] = new Option(name.substr(0,50), audio.deviceId);
        audioSelect2.options[audioSelect2.options.length] = new Option(name.substr(0,50), audio.deviceId);
    });

    videos.forEach(video => {
        let name = video.label;
        if (name === "") name = video.deviceId;
        videoSelect.options[videoSelect.options.length] = new Option(name.substr(0,50), video.deviceId);
        videoSelect2.options[videoSelect2.options.length] = new Option(name.substr(0,50), video.deviceId);
    });

    videoSelect.selectedIndex = config['currentVideoSourceIndex'];
    videoSelect2.selectedIndex = config['currentVideoSource2Index']+1;
    audioSelect.selectedIndex = config['currentAudioSourceIndex'];
    audioSelect2.selectedIndex = config['currentAudioSource2Index']+1;
}

function configDialogClosed(){
    // Compare values with current config and apply changes if needed
    let videoSelect = $('#videoSelect')[0];
    let audioSelect = $('#audioSelect')[0];
    let videoSelect2 = $('#videoSelect2')[0];
    let audioSelect2 = $('#audioSelect2')[0];
    let mirrorCheck = $('#mirrorCheck')[0];

    if (videoSelect.selectedIndex !== currentConfig['currentVideoSourceIndex'] ||
        audioSelect.selectedIndex !== currentConfig['currentAudioSourceIndex']){
        // Video and/or audio source changed
        currentConfig['currentVideoSourceIndex'] = videoSelect.selectedIndex;
        currentConfig['currentAudioSourceIndex'] = audioSelect.selectedIndex;
        updateLocalAudioVideoSource(1);
    }

    if (mirrorCheck.checked !== currentConfig['video1Mirror']){
        // Mirror changed
        currentConfig['video1Mirror'] = mirrorCheck.checked;
        setMirror(currentConfig['video1Mirror'], true, 1);
    }

    if (videoSelect2.selectedIndex !== currentConfig['currentVideoSource2Index'] ||
        audioSelect2.selectedIndex !== currentConfig['currentAudioSource2Index']
    ){
        // Secondary audio/video source changed
        currentConfig['currentVideoSource2Index'] = videoSelect2.selectedIndex-1;
        currentConfig['currentAudioSource2Index'] = audioSelect2.selectedIndex-1;
    }
}

function setTitle(local, index, title){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let label = $('#' + view_prefix + 'ViewTitle' + index);
    if (title === undefined) title = "Participant #" + index;
    if (label.length){
        label[0].innerText = title;
    }
}

function getTitle(local, index){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let label = $('#' + view_prefix + 'ViewTitle' + index);
    let title = "Participant #" + index;
    if (label.length){
        title =  label[0].innerText;
    }
    return title;
}

function showPTZControls(local, index, zoom, presets, settings){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let zoomControls = $("#" + view_prefix + "ZoomButtons" + index);
    let presetControls = $("#" + view_prefix + "PresetButtons" + index);
    let settingsControl = $("#" + view_prefix + "SettingsButton" + index);

    (zoom === true) ? zoomControls.show() : zoomControls.hide();
    (presets === true) ? presetControls.show() : presetControls.hide();
    (settings === true) ? settingsControl.show() : settingsControl.hide();
}

function hasPTZControls(local, index){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let zoomControls = $("#" + view_prefix + "ZoomButtons" + index);
    let presetControls = $("#" + view_prefix + "PresetButtons" + index);
    let settingsControl = $("#" + view_prefix + "SettingsButton" + index);

    return zoomControls.css('display') !== 'none' ||
        presetControls.css('display') !== 'none' ||
        settingsControl.css('display') !== 'none';

}

function refreshRemoteStatusIcons(peerid){
    let card_index = getContactIndexForPeerId(peerid);
    let index = getStreamIndexForPeerId(peerid, 'default'); // Get default stream id

    if (card_index === undefined){
        console.log('refreshRemoteStatusIcons - no contact information for ' + peerid );
        return;
    }

    if (index === undefined){
        console.log('refreshRemoteStatusIcons - no stream for ' + peerid);
        return;
    }

    let status = remoteContacts[card_index].status;

    if (status.micro !== undefined) {
        updateStatusIconState(status.micro, false, index + 1, "Mic");
    }

    if (status.micro2 !== undefined){
        let index2 = getStreamIndexForPeerId(peerid, "2ndStream");
        if (index2)
            updateStatusIconState(status.micro2, false, index2+1, "Mic");
    }

    if (status.speaker !== undefined) {
        updateStatusIconState(status.speaker, false, index + 1, "Speaker");
    }

    if (status.video !== undefined) {
        updateStatusIconState(status.video, false, index + 1, "Video");
    }

    if (status.primaryView !== undefined){
        if (isParticipant){
            if (status.primaryView.peerid !== 0){
                index = getStreamIndexForPeerId(peerid, status.primaryView.streamName);
            }

            if (index !== undefined){
                let local = (status.primaryView.peerid === local_peerid);
                let view_id = getVideoViewId(local, index+1);
                setLargeView(view_id);

            }else{
                // Defaults to first remote view
                setLargeView('remoteView1');

            }
       }
        primaryView = status.primaryView;
        setPrimaryViewIcon(status.primaryView.peerid, status.primaryView.streamName);
    }
}

function getVideoViewId(local, index){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    return view_prefix + "View" + index;
}

function muteMicroAll(){
    let mute = !isIconActive("btnMicAll");
    for (let i=1; i<=remoteStreams.length; i++){
        muteMicro(false, i, mute);
    }
    setIconState("btnMicAll", 'Mic', mute);
}

function muteSpeakerAll(){
    let mute = !isIconActive("btnSpeakerAll");
    for (let i=1; i<=remoteStreams.length; i++){
        muteSpeaker(false, i, mute);
    }
    setIconState("btnSpeakerAll", 'Speaker', mute);
}

function showChronosDialog(){
    let partSelect = $('#chronosPartSelect')[0];
    partSelect.options.length = 0;
    partSelect.options[partSelect.options.length] = new Option("Tous", "0");

    for (let i=0; i<remoteContacts.length; i++){
        let index = getStreamIndexForPeerId(remoteContacts[i].peerid, 'default');
        if (index !== undefined){
            partSelect.options[partSelect.options.length] = new Option(getTitle(false, index+1), index+1);
        }
    }

    $('#chronosDialog').modal('show');

}

function showTextDisplay(local, index, show){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let display = $('#' + view_prefix + 'Display' + index);
    if (display.length){
        (show) ? display.show() : display.hide();
    }
}

function setTextDisplay(local, index, text){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let display = $('#' + view_prefix + 'Text' + index);
    if (display.length){
        display[0].innerHTML = text;
    }
}

function getTextDisplay(local, index){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let display = $('#' + view_prefix + 'Text' + index);
    if (display.length){
        return display[0].innerHTML;
    }
}

function selectPrimaryView(local, index){
    // Get stream name
    let streamName = 'default';
    let btnSelected = isButtonActive(local, index, 'Star');
    let peer_id = 0;
    if (local === true){
        streamName = localStreams[index-1].streamname;
        if (!btnSelected){
            peer_id = local_peerid;
        }
    }else{
        streamName = remoteStreams[index-1].streamname;
        if (!btnSelected){
            peer_id = remoteStreams[index-1].peerid;
        }
    }
    setPrimaryView(peer_id, streamName);
    setPrimaryViewIcon(peer_id, streamName);
}

function setPrimaryViewIcon(peer_id, streamName){
    let local = (peer_id === local_peerid);
    // Browse all streams, and set icon accordingly
    for (let i=0; i<localStreams.length; i++){
        if (local === true && localStreams[i].streamname === streamName){
            updateButtonIconState(true, true, i+1, 'Star');
        }else{
            updateButtonIconState(false, true, i+1, 'Star');
        }
    }

    for (let i=0; i<remoteStreams.length; i++){
        if (local === false && remoteStreams[i].peerid === peer_id && remoteStreams[i].streamname === streamName){
            updateButtonIconState(true, false, i+1, 'Star');
        }else{
            updateButtonIconState(false, false, i+1, 'Star');
        }
    }
}

function playSound(soundname){
    if (isWeb){
        document.getElementById(soundname).play();
    }
}

function stopSounds(){
    document.getElementById("audioConnected").pause();
    document.getElementById("audioDisconnected").pause();
    document.getElementById("audioCalling").pause();
}