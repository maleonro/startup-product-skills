import subprocess,numpy as np,glob,sys,os,imageio_ffmpeg
F=imageio_ffmpeg.get_ffmpeg_exe()
files=sys.argv[1:]
for f in files:
    p=subprocess.run([F,'-v','error','-i',f,'-vf','fps=10,scale=64:36,format=gray','-f','rawvideo','-'],capture_output=True)
    a=np.frombuffer(p.stdout,dtype=np.uint8).reshape(-1,36,64).astype(np.float32)
    d=np.abs(np.diff(a,axis=0)).mean(axis=(1,2))
    static=(d<0.4).mean()*100
    # longest static run in seconds
    run=best=0
    for x in d:
        run=run+1 if x<0.4 else 0; best=max(best,run)
    print(f"{os.path.basename(f):28s} frames={len(a):4d} meanDiff={d.mean():5.2f} static%={static:5.1f} longestHold={best/10:4.1f}s")
