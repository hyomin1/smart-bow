import { useEffect, useRef } from 'react';
import { api } from '../api/axios';

interface Props {
  camId: string;
}

export default function CamWebRTC({ camId }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  console.log('dev 확인');
  useEffect(() => {
    //const pc = new RTCPeerConnection();
    const pc = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        {
          urls: `turn:${import.meta.env.VITE_TURN_SERVER}:3478?transport=udp`,
          username: import.meta.env.VITE_TURN_USERNAME,
          credential: import.meta.env.VITE_TURN_CREDENTIAL,
        },
      ],
    });

    setInterval(async () => {
      const stats = await pc.getStats();
      stats.forEach((report) => {
        if (report.type === 'inbound-rtp' && report.mediaType === 'video') {
          console.log(
            '비트레이트:',
            Math.round((report.bytesReceived * 8) / 1024 / 1024),
            'Mbps'
          );
          console.log('FPS:', report.framesPerSecond);
          console.log('패킷 손실:', report.packetsLost);
          console.log('코덱 ID:', report.codecId);
        }

        // 코덱 상세 정보
        if (report.type === 'codec' && report.mimeType.includes('video')) {
          console.log('코덱 정보:', report.mimeType, report.sdpFmtpLine);
        }
      });
    }, 3000);

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

      const resp = await api.post(`webrtc/offer/${camId}`, pc.localDescription);

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
      controls
      className='w-full h-full bg-black object-cover'
    />
  );
}
