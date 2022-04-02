#!/usr/bin/liquidsoap

#postprocessing function
def orban(dry)

    radio = normalize(target=-17., window = 0.03, gain_min= -32., gain_max = 0., dry)
    
    #multiband compressor
    #radio = compress.multiband.interactive(id="vitalizer",radio)

    # Initial compression low ration
    comp_attack = interactive.float(min=0.,max=20.,step=0.5,"comperssor_attack",unit="ms",0.5)
    comp_release = interactive.float(min=1.,max=500.,step=1.,"comperssor_release",unit="ms",1.0)
    comp_thr = interactive.float(min=-60.,max=0.,step=1.,"comperssor_threshold",unit="dB",-36.0)
    comp_ratio = interactive.float(min=1.,max=10.,step=0.1,"comperssor_ratio",unit="",1.0)
    comp_gain = interactive.float(min=-20.,max=10.,step=0.1,"comperssor_gain",unit="dB",0.)
    comp_window = interactive.float(min=0.,max=10.,step=0.1,"comperssor_window",unit="s",0.)
    
    radio = compress(attack = comp_attack, release = comp_release, threshold = comp_thr, ratio=comp_ratio, gain = comp_gain, window = comp_window, clip(radio))

    wet = limit(radio)

    c = interactive.float("wetness", min=0., max=1., 1.)
    output = dry_wet(c, dry, wet)
    
    #set web service
    interactive.harbor(port=11000)

    #backup set data
    interactive.persistent("/var/log/emiter/orban.json")

    #return output
    clip(output)
end
