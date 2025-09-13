import LiveStreamerViewer from './components/LiveStreamerViewer';
import TargetOverlayView from './components/TargetOverlayView';

export default function App() {
  return (
    <div className='flex h-screen'>
      <div className='w-1/2 h-full'>
        <LiveStreamerViewer />
      </div>
      <div className='w-1/2 h-full'>
        <TargetOverlayView />
      </div>
    </div>
  );
}
