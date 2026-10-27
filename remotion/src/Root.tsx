import React from "react";
import { Composition } from "remotion";
import { PackMV } from "./PackMV";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="PackMV"
      component={PackMV as any}
      defaultProps={{ song: "", fps: 24, total_frames: 24, shots: [], lyrics: [] } as any}
      calculateMetadata={({ props }: any) => ({ durationInFrames: props.total_frames, fps: props.fps })}
      fps={24}
      width={1920}
      height={1080}
    />
  );
};
