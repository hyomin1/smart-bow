import { useEffect, forwardRef, useImperativeHandle, useRef } from 'react';
import { api } from '../api/axios';

interface Props {
  camId: string;
  cover?: boolean;
}

const CamWebRTC = forwardRef<HTMLVideoElement, Props>(
  ({ camId, cover }, ref) => {
    const videoRef = useRef<HTMLVideoElement>(null);

    useImperativeHandle(ref, () => videoRef.current as HTMLVideoElement);
    useEffect(() => {
      //const pc = new RTCPeerConnection();
      const pc = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          {urls: 'stun:stun.cloudflare.com:3478' },
          {
           urls: [
        `turn:${import.meta.env.VITE_TURN_SERVER}:3478?transport=udp`,
        `turn:${import.meta.env.VITE_TURN_SERVER}:3478?transport=tcp`,
      ],
            username: import.meta.env.VITE_TURN_USERNAME,
            credential: import.meta.env.VITE_TURN_CREDENTIAL,
          },
        ],
        iceCandidatePoolSize: 8,
      });

      // 서버에서 오는 스트림 붙이기
      pc.oniceconnectionstatechange = () => {
        console.log('ICE Connection State:', pc.iceConnectionState);
      };

      pc.onicegatheringstatechange = () => {
        console.log('ICE Gathering State:', pc.iceGatheringState);
      };

      pc.onicecandidate = (event) => {
        if (event.candidate) {
          console.log('ICE Candidate:', event.candidate);
        }
      };
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

        const resp = await api.post(
          `webrtc/offer/${camId}`,
          pc.localDescription
        );

        const answer = await resp.data;

        await pc.setRemoteDescription(answer);
      }

      start();
    }, [camId]);

    return (
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className={`w-full h-full bg-black ${
          cover ? 'object-cover' : 'object-contain'
        }`}
      />
    );
  }
);
export default CamWebRTC;
