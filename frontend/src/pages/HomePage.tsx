import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ROUTES } from '../../constants/routes';

export default function HomePage() {
  const targets = [
    {
      id: 'target1',
      name: '1관',
      color: 'from-cyan-400 to-blue-500',
      glowColor: 'rgba(0, 255, 255, 0.4)',
      borderColor: 'border-cyan-400',
    },
    {
      id: 'target2',
      name: '2관',
      color: 'from-pink-400 to-purple-500',
      glowColor: 'rgba(236, 72, 153, 0.4)',
      borderColor: 'border-pink-400',
    },
    {
      id: 'target3',
      name: '3관',
      color: 'from-violet-400 to-indigo-500',
      glowColor: 'rgba(139, 92, 246, 0.4)',
      borderColor: 'border-violet-400',
    },
    {
      id: 'target-test',
      name: 'TEST',
      color: 'from-yellow-400 to-orange-500',
      glowColor: 'rgba(255, 215, 0, 0.4)',
      borderColor: 'border-yellow-400',
    },
  ];

  return (
    <div className='relative min-h-screen bg-black overflow-hidden'>
      {/* Animated background */}
      <div className='absolute inset-0 bg-gradient-to-br from-purple-950 via-black to-cyan-950 opacity-60' />

      {/* Grid overlay */}
      <div
        className='absolute inset-0 opacity-10'
        style={{
          backgroundImage: `
            linear-gradient(0deg, transparent 24%, rgba(0, 255, 255, 0.3) 25%, rgba(0, 255, 255, 0.3) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, 0.3) 75%, rgba(0, 255, 255, 0.3) 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, rgba(0, 255, 255, 0.3) 25%, rgba(0, 255, 255, 0.3) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, 0.3) 75%, rgba(0, 255, 255, 0.3) 76%, transparent 77%, transparent)
          `,
          backgroundSize: '60px 60px',
        }}
      />

      {/* Scanline effect */}
      <motion.div
        className='absolute inset-0 pointer-events-none'
        style={{
          background:
            'linear-gradient(0deg, transparent 0%, rgba(0, 255, 255, 0.03) 50%, transparent 100%)',
          backgroundSize: '100% 4px',
        }}
        animate={{ y: [0, 100] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
      />

      <div className='relative z-10 container mx-auto px-6 py-12'>
        {/* Header */}
        <motion.div
          className='text-center mb-20'
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className='inline-block mb-6'
            animate={{
              textShadow: [
                '0 0 20px rgba(0, 255, 255, 0.5)',
                '0 0 40px rgba(0, 255, 255, 0.8)',
                '0 0 20px rgba(0, 255, 255, 0.5)',
              ],
            }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <h1 className='text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-pink-400 to-cyan-400 tracking-wider font-mono'>
              스마트 국궁
            </h1>
          </motion.div>

          <motion.div
            className='flex items-center justify-center gap-3'
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <motion.div
              className='w-16 h-0.5 bg-gradient-to-r from-transparent to-cyan-400'
              animate={{ scaleX: [0, 1] }}
              transition={{ duration: 1, delay: 0.5 }}
            />
            <span className='text-cyan-400 font-mono text-sm tracking-widest'>
              ARCHERY SYSTEM
            </span>
            <motion.div
              className='w-16 h-0.5 bg-gradient-to-l from-transparent to-cyan-400'
              animate={{ scaleX: [0, 1] }}
              transition={{ duration: 1, delay: 0.5 }}
            />
          </motion.div>
        </motion.div>

        {/* Target selection */}
        <div className='max-w-6xl mx-auto'>
          <motion.div
            className='text-center mb-12'
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <h2 className='text-3xl font-bold text-white font-mono mb-2 tracking-wide'>
              관을 선택해주세요
            </h2>
            <div className='w-32 h-1 bg-gradient-to-r from-transparent via-pink-500 to-transparent mx-auto' />
          </motion.div>

          <div className='grid md:grid-cols-2 lg:grid-cols-4 gap-6'>
            {targets.map((target, index) => (
              <motion.div
                key={target.id}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
              >
                <Link
                  to={ROUTES.STREAM(target.id)}
                  className='group block relative'
                >
                  {/* Glow effect on hover */}
                  <motion.div
                    className='absolute -inset-1 rounded-lg opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500'
                    style={{
                      background: `linear-gradient(135deg, ${target.glowColor}, transparent)`,
                    }}
                  />

                  {/* Main card */}
                  <div className='relative bg-black border-2 ${target.borderColor} rounded-lg overflow-hidden'>
                    {/* Corner decorations */}
                    <div
                      className={`absolute top-0 left-0 w-6 h-6 border-t-2 border-l-2 ${target.borderColor}`}
                    />
                    <div
                      className={`absolute top-0 right-0 w-6 h-6 border-t-2 border-r-2 ${target.borderColor}`}
                    />
                    <div
                      className={`absolute bottom-0 left-0 w-6 h-6 border-b-2 border-l-2 ${target.borderColor}`}
                    />
                    <div
                      className={`absolute bottom-0 right-0 w-6 h-6 border-b-2 border-r-2 ${target.borderColor}`}
                    />

                    {/* Content */}
                    <div className='relative p-8'>
                      {/* Status indicator */}
                      <div className='absolute top-3 right-3 flex items-center gap-1'>
                        <motion.div
                          className='w-2 h-2 rounded-full bg-green-400'
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 2, repeat: Infinity }}
                          style={{ boxShadow: '0 0 10px #4ade80' }}
                        />
                        <span className='text-green-400 text-xs font-mono'>
                          LIVE
                        </span>
                      </div>

                      {/* Target name */}
                      <div className='text-center mb-6 mt-4'>
                        <motion.h3
                          className={`text-5xl font-bold bg-gradient-to-br ${target.color} bg-clip-text text-transparent mb-2 font-mono`}
                          whileHover={{ scale: 1.1 }}
                          transition={{ type: 'spring', stiffness: 300 }}
                        >
                          {target.name}
                        </motion.h3>
                        <div
                          className={`w-16 h-1 bg-gradient-to-r ${target.color} mx-auto`}
                        />
                      </div>

                      {/* Info */}
                      <div className='space-y-2 text-center'>
                        <div className='flex items-center justify-center gap-2'>
                          <div className='flex gap-1'>
                            {[...Array(3)].map((_, i) => (
                              <motion.div
                                key={i}
                                className={`w-1 h-3 bg-gradient-to-t ${target.color}`}
                                animate={{ scaleY: [0.5, 1, 0.5] }}
                                transition={{
                                  duration: 1,
                                  repeat: Infinity,
                                  delay: i * 0.1,
                                }}
                              />
                            ))}
                          </div>
                          <span className='text-xs text-gray-500 font-mono'>
                            SIGNAL
                          </span>
                        </div>
                      </div>

                      <motion.div
                        className={`absolute inset-0 bg-gradient-to-br ${target.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
                      />

                      <motion.div
                        className='absolute bottom-3 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity'
                        animate={{ y: [0, 5, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      >
                        <div
                          className={`text-xs font-mono text-gray-400 border border-gray-600 px-3 py-1 rounded-full bg-black bg-opacity-50`}
                        >
                          입장 →
                        </div>
                      </motion.div>
                    </div>

                    {/* Animated border effect */}
                    <motion.div
                      className={`absolute inset-0 border-2 ${target.borderColor} opacity-0 group-hover:opacity-100 rounded-lg`}
                      animate={{
                        boxShadow: [
                          `0 0 10px ${target.glowColor}`,
                          `0 0 20px ${target.glowColor}`,
                          `0 0 10px ${target.glowColor}`,
                        ],
                      }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
