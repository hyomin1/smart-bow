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
      const pc = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun.cloudflare.com:3478' },
          {
            urls: [
              `turn:${import.meta.env.VITE_TURN_SERVER}:3478?transport=udp`,
              `turn:${import.meta.env.VITE_TURN_SERVER}:3478?transport=tcp`,
            ],
            username: import.meta.env.VITE_TURN_USERNAME,
            credential: import.meta.env.VITE_TURN_CREDENTIAL,
          },
        ],
      });

      // 🔥 필수 로그 4개만 남긴다
      pc.oniceconnectionstatechange = () => {
        console.log('🧊 ICE State:', pc.iceConnectionState);
      };

      pc.onicegatheringstatechange = () => {
        console.log('📡 ICE Gathering:', pc.iceGatheringState);
      };

      pc.ontrack = (event) => {
        console.log('🎥 ontrack fired! streams:', event.streams);
        const videoEl = videoRef.current;

        if (!videoEl) return;

        videoEl.srcObject = event.streams[0];

        videoEl.onloadedmetadata = () => {
          videoEl.play().catch((err) => {
            console.error('❌ video play() failed:', err);
          });
        };
      };

      pc.onicecandidate = (event) => {
        if (event.candidate) {
          console.log('📨 ICE Candidate:', event.candidate);
        }
      };

      async function start() {
        // 🔥 Chrome/aiortc 안정화의 핵심
        pc.addTransceiver('video', { direction: 'recvonly' });

        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        const resp = await api.post(
          `webrtc/offer/${camId}`,
          pc.localDescription
        );
        const answer = resp.data;

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
