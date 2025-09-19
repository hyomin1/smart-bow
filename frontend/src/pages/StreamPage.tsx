import CamWebRTC from '../components/CamWebRTC';
import { useParams } from 'react-router-dom';
import TargetOverlayView from '../components/TargetOverlayView';

export default function StreamPage() {
  const { camId } = useParams();

  if (!camId) {
    return <span>잘못된 카메라 경로입니다</span>;
  }
  return (
    <div>
      <div className='flex h-screen'>
        <div className='w-1/2 h-full'>
          <CamWebRTC camId={camId} />
        </div>
        <div className='w-1/2 h-full'>
          <TargetOverlayView camId={camId} />
        </div>
      </div>
    </div>
  );
}
