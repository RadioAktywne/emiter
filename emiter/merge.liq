#!/home/liquidsoap/.opam/4.08.0/bin/liquidsoap
set("log.stdout",true)

list_filenames = argv(default="",1)
file_out = argv(default="",2)

filenames = string.split(separator="@",list_filenames)
files = ref([])

#print(list_filenames)

def add_file_in(file)
    #print(file)
    files := list.append(!files,[once(single(file))])
end
list.iter(add_file_in,filenames)

fullfile = sequence(!files)
clock.assign_new(sync="none",[fullfile])

output.file(%vorbis, file_out,fallible=true,
                     on_stop=shutdown,fullfile)   
