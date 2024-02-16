# boosted_tau_shaper
Repository for boosted H -> tau tau control plots and scale factors measurement 

One can produce control plots in two steps: produce shapes and pictures
The example of shape production command :

```
bash control_plots_ul_htt_boost.sh mt 2016postVFP htautau_boost_Feb12_nlo_genw_with_trg_match  processes_separately  SHAPES
```

- `mt` is a final state (et, tt)
- `2016postVFP` is a data-taking period, could be 2016preVFP, 2017, 2018
- `htautau_boost_Feb12_nlo_genw_with_trg_match` is a ntuple tag (shpuld be the same as you used to produced ntuples via CROWN), 
- `processes_separately` - tag you are free to choose whatever you like but it it's better when tag reflects the content of 
piclures. 

Then you can produce plots:

```
bash control_plots_ul_htt_boost.sh mt 2016postVFP htautau_boost_Feb12_nlo_genw_with_trg_match  processes_separately PLOT
```