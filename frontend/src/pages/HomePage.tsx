import { Link } from 'react-router-dom';
import { ROUTES } from '../../constants/routes';

export default function HomePage() {
  //TODO: 추후 서버에서 정보 받아서 스트리밍 되는 관만 보여주기
  return (
    <div className='min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900'>
      <div className='container mx-auto px-6 py-12'>
        <div className='text-center mb-16'>
          <h1 className='text-6xl font-bold text-white mb-4 tracking-tight'>
            스마트 국궁
          </h1>
        </div>

        <div className='max-w-4xl mx-auto'>
          <h2 className='text-3xl font-semibold text-white text-center mb-12'>
            활터 선택
          </h2>

          <div className='grid md:grid-cols-3 gap-8'>
            {[
              {
                id: 'target1',
                name: '1관',
                color: 'from-emerald-500 to-teal-600',
              },
              {
                id: 'target2',
                name: '2관',
                color: 'from-amber-500 to-orange-600',
              },
              {
                id: 'target3',
                name: '3관',
                color: 'from-purple-500 to-indigo-600',
              },
            ].map((target) => (
              <Link
                key={target.id}
                to={ROUTES.STREAM(target.id)}
                className='group relative overflow-hidden rounded-2xl shadow-2xl transform transition-all duration-300 hover:scale-105 hover:shadow-3xl'
              >
                <div
                  className={`bg-gradient-to-br ${target.color} p-8 text-white relative z-10`}
                >
                  <div className='text-center'>
                    <h3 className='text-3xl font-bold mb-2'>{target.name}</h3>
                    <p className='text-lg opacity-90'>실시간 스트리밍</p>
                  </div>

                  <div className='absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity duration-300' />

                  <div className='absolute -top-4 -right-4 w-24 h-24 bg-white opacity-10 rounded-full' />
                  <div className='absolute -bottom-6 -left-6 w-32 h-32 bg-white opacity-5 rounded-full' />
                </div>

                <div
                  className={`absolute inset-0 bg-gradient-to-br ${target.color} opacity-0 group-hover:opacity-20 blur-xl transition-all duration-500 -z-10`}
                />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
