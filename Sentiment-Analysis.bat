import './App.css';
import { useEffect, useState, useRef } from "react";

function App() {
  const width = 500;
  const height = 500;
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [downloadAnchorVisible, setDownloadAnchorVisible] = useState(null);
  let chunks = [];
  var downloadlink = useRef(null);

  useEffect(() => {
    if (mediaRecorder) {
      mediaRecorder.ondataavailable = function (ev) {
        chunks.push(ev.data);
      };
    }

    if (mediaRecorder && !downloadAnchorVisible) {
      mediaRecorder.start();
    }

    if (downloadAnchorVisible) {
      let video = document.getElementsByClassName("app_videoFeed")[0];
      downloadlink.current = document.querySelector("a[ download ]");

      mediaRecorder.onstop = (ev) => {
        let blob = new Blob(chunks, { 'type': 'video/mp4;' });
        let videoURL = window.URL.createObjectURL(blob);
        video.src = videoURL;
        downloadlink.current.setAttribute("href", videoURL);
      };
    }
    // eslint-disable-next-line
  }, [mediaRecorder, downloadAnchorVisible]);

  const startVideoRecording = () => {
    navigator.mediaDevices.getUserMedia(
      { video: true, audio: true }
    )
      .then((stream) => {
        let video = document.getElementsByClassName("app_videoFeed")[0];
        if (video) {
          video.srcObject = stream;
          setMediaRecorder(new MediaRecorder(stream));
        }
      })
      .catch((error) => {
        console.log(error);
      });
    setDownloadAnchorVisible(false);
    chunks = [];
  };

  const endVideoRecording = () => {
    let video = document.getElementsByClassName("app_videoFeed")[0];
    if (mediaRecorder && video.srcObject) {
      mediaRecorder.stop();

      if (downloadAnchorVisible === false) {
        setDownloadAnchorVisible(true);
      }
    }
    video.srcObject = null;
  };

  return (
    <div className="app">
      <div className="app_container">
        <video
          className="app_videoFeed"
          height={height}
          width={width}
          autoPlay
        />
      </div>
      <div className='app_input'>
        <button onClick={startVideoRecording}>
          Play Video
        </button>
        <button onClick={endVideoRecording}>
          Stop Video
        </button>
        {downloadAnchorVisible
          &&
          <a href="titties" download="data">
            Download Video
          </a>
        }
      </div>
    </div>
  );
}

export default App;
