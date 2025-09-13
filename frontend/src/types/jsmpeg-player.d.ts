declare module '@cycjimmy/jsmpeg-player' {
  export interface PlayerOptions {
    canvas?: HTMLCanvasElement;
    autoplay?: boolean;
    audio?: boolean;
    loop?: boolean;
    pauseWhenHidden?: boolean;
    disableGl?: boolean;
    preserveDrawingBuffer?: boolean;
    progressive?: boolean;
    throttled?: boolean;
  }

  export class Player {
    constructor(url: string | WebSocket, options?: PlayerOptions);
    play(): void;
    pause(): void;
    stop(): void;
    destroy(): void;
  }

  const JSMpeg: {
    Player: typeof Player;
  };

  export default JSMpeg;
}
