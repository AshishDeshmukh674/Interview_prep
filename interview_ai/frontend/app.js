async function uploadResume() {
    let file = document.getElementById("resumeUpload").files[0];
    let formData = new FormData();
    formData.append("file", file);

    let response = await fetch("/upload_resume/", { method: "POST", body: formData });
    let data = await response.json();
    alert("Interview Questions: " + JSON.stringify(data.questions));
}

async function startRecording() {
    let stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    document.getElementById("video").srcObject = stream;
}
