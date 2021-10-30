#!/usr/bin/liquidsoap

#postprocessing function
def orban(radio)

    # radio = normalize(target=-17., window = 0.03, gain_min= -32., gain_max = 0., radio)
    
    #podobno jakiś multiband compressor, jakoś to brzmi ale dupska nie urywa
    #radio = compress.multiband.interactive(id="vitalizer",radio)

    # Initial compression low ration
    radio = compress(attack = 0.5, release = 1., threshold = -36.0, ratio=1., gain = 6., radio)

    limit(radio)
end