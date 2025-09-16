import LiveStreamerViewer from './components/CamHlsPlayer';
import CamWebRTC from './components/CamWebRTC';
import TargetOverlayView from './components/TargetOverlayView';

export default function App() {
  return (
    <div className='flex h-screen'>
      <div className='w-1/2 h-full'>
        {/* <LiveStreamerViewer /> */}
        <CamWebRTC />
      </div>
      <div className='w-1/2 h-full'>
        <TargetOverlayView />
      </div>
    </div>
  );
}
