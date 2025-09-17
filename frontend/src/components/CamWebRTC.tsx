import { useEffect, useRef } from 'react';
import { api } from '../api/axios';

export default function CamWebRTC() {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const pc = new RTCPeerConnection();

    // 서버에서 오는 스트림 붙이기
    pc.ontrack = (event) => {
      if (videoRef.current) {
        videoRef.current.srcObject = event.streams[0];
      }
    };

    // 브라우저 ICE candidate 확인
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        //console.log('ICE candidate:', event.candidate);
      }
    };

    async function start() {
      const offer = await pc.createOffer({
        offerToReceiveAudio: false,
        offerToReceiveVideo: true,
      });
      await pc.setLocalDescription(offer);

      const resp = await api.post('webrtc/offer', pc.localDescription);

      const answer = await resp.data;
      await pc.setRemoteDescription(answer);
    }

    start();
  }, []);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      controls
      className='w-full h-full bg-black object-contain'
    />
  );
}
