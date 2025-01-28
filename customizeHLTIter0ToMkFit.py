import FWCore.ParameterSet.Config as cms

import RecoTracker.MkFit.mkFitGeometryESProducer_cfi as mkFitGeometryESProducer_cfi
import RecoTracker.MkFit.mkFitSiPixelHitConverter_cfi as mkFitSiPixelHitConverter_cfi
import RecoTracker.MkFit.mkFitSiStripHitConverter_cfi as mkFitSiStripHitConverter_cfi
import RecoTracker.MkFit.mkFitEventOfHitsProducer_cfi as mkFitEventOfHitsProducer_cfi
import RecoTracker.MkFit.mkFitSeedConverter_cfi as mkFitSeedConverter_cfi
import RecoTracker.MkFit.mkFitIterationConfigESProducer_cfi as mkFitIterationConfigESProducer_cfi
import RecoTracker.MkFit.mkFitProducer_cfi as mkFitProducer_cfi
import RecoTracker.MkFit.mkFitOutputConverter_cfi as mkFitOutputConverter_cfi
import RecoLocalTracker.SiStripRecHitConverter.SiStripRecHitConverter_cfi as SiStripRecHitConverter_cfi


def customizeHLTIter0ForIterL3Muon(process):
    for objLabel in [
            'hltSiStripRawToClustersFacility',
            'HLTDoLocalStripSequence',
            'HLTIterativeTrackingIteration0ForIterL3Muon',
            'hltIter0IterL3MuonCkfTrackCandidates',
    ]:
        if not hasattr(process, objLabel):
            print(f'# WARNING: customizeHLTIter0ForIterL3Muon failed (object with label "{objLabel}" not found) - no customisation applied !')
            return process


    # mkFit needs all clusters, so switch off the on-demand mode
    process.hltSiStripRawToClustersFacility = cms.EDProducer(
        "SiStripClusterizerFromRaw",
        ProductLabel = cms.InputTag( "rawDataCollector" ),
        ConditionsLabel = cms.string( "" ),
        onDemand = cms.bool( True ),
        DoAPVEmulatorCheck = cms.bool( False ),
        LegacyUnpacker = cms.bool( False ),
        HybridZeroSuppressed = cms.bool( False ),
        Clusterizer = cms.PSet( 
            ConditionsLabel = cms.string( "" ),
            MaxClusterSize = cms.uint32( 32 ), 
            ClusterThreshold = cms.double( 5.0 ),
            SeedThreshold = cms.double( 3.0 ),
            Algorithm = cms.string( "ThreeThresholdAlgorithm" ),
            ChannelThreshold = cms.double( 2.0 ),
            MaxAdjacentBad = cms.uint32( 0 ),
            setDetId = cms.bool( True ),
            MaxSequentialHoles = cms.uint32( 0 ),
            RemoveApvShots = cms.bool( True ),
            clusterChargeCut = cms.PSet(  refToPSet_ = cms.string( "HLTSiStripClusterChargeCutNone" ) ),
            MaxSequentialBad = cms.uint32( 1 )
        ),
        Algorithms = cms.PSet( 
            Use10bitsTruncation = cms.bool( False ),
            CommonModeNoiseSubtractionMode = cms.string( "Median" ),
            useCMMeanMap = cms.bool( False ),
            TruncateInSuppressor = cms.bool( True ),
            doAPVRestore = cms.bool( False ),
            SiStripFedZeroSuppressionMode = cms.uint32( 4 ),
            PedestalSubtractionFedMode = cms.bool( True )
        )
    )
    process.hltSiStripRawToClustersFacility.onDemand = False
    process.hltSiStripRawToClustersFacility.Clusterizer.MaxClusterSize = 8

    process.hltSiStripRecHits = SiStripRecHitConverter_cfi.siStripMatchedRecHits.clone(
        ClusterProducer = "hltSiStripRawToClustersFacility",
        StripCPE = "hltESPStripCPEfromTrackAngle:hltESPStripCPEfromTrackAngle",
        doMatching = False,
    )

    # Use fourth hit if one is available
    process.hltIter0IterL3MuonPixelSeedsFromPixelTracks.includeFourthHit = cms.bool(True)

    process.load("RecoTracker.MkFit.mkFitGeometryESProducer_cfi")

    process.hltIter0IterL3MuonCkfTrackCandidatesMkFitSiPixelHits = mkFitSiPixelHitConverter_cfi.mkFitSiPixelHitConverter.clone(
        hits = "hltSiPixelRecHits",
        clusters = "hltSiPixelClusters",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0IterL3MuonCkfTrackCandidatesMkFitSiStripHits = mkFitSiStripHitConverter_cfi.mkFitSiStripHitConverter.clone(
        rphiHits = "hltSiStripRecHits:rphiRecHit",
        stereoHits = "hltSiStripRecHits:stereoRecHit",
        clusters = "hltSiStripRawToClustersFacility",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutLoose'),
    )
    process.hltIter0IterL3MuonCkfTrackCandidatesMkFitEventOfHits = mkFitEventOfHitsProducer_cfi.mkFitEventOfHitsProducer.clone(
        beamSpot  = "hltOnlineBeamSpot",
        pixelHits = "hltIter0IterL3MuonCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0IterL3MuonCkfTrackCandidatesMkFitSiStripHits",
    )
    process.hltIter0IterL3MuonCkfTrackCandidatesMkFitSeeds = mkFitSeedConverter_cfi.mkFitSeedConverter.clone(
        seeds = "hltIter0IterL3MuonPixelSeedsFromPixelTracksFiltered",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0IterL3MuonTrackCandidatesMkFitConfig = mkFitIterationConfigESProducer_cfi.mkFitIterationConfigESProducer.clone(
        ComponentName = 'hltIter0IterL3MuonTrackCandidatesMkFitConfig',
        config = 'RecoTracker/MkFit/data/mkfit-phase1-initialStep.json',
    )
    process.hltIter0IterL3MuonCkfTrackCandidatesMkFit = mkFitProducer_cfi.mkFitProducer.clone(
        pixelHits = "hltIter0IterL3MuonCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0IterL3MuonCkfTrackCandidatesMkFitSiStripHits",
        eventOfHits = "hltIter0IterL3MuonCkfTrackCandidatesMkFitEventOfHits",
        seeds = "hltIter0IterL3MuonCkfTrackCandidatesMkFitSeeds",
        config = ('', 'hltIter0IterL3MuonTrackCandidatesMkFitConfig'),
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutNone'),
    )
    process.hltIter0IterL3MuonCkfTrackCandidates = mkFitOutputConverter_cfi.mkFitOutputConverter.clone(
        seeds = "hltIter0IterL3MuonPixelSeedsFromPixelTracksFiltered",
        mkFitEventOfHits = "hltIter0IterL3MuonCkfTrackCandidatesMkFitEventOfHits",
        mkFitPixelHits = "hltIter0IterL3MuonCkfTrackCandidatesMkFitSiPixelHits",
        mkFitStripHits = "hltIter0IterL3MuonCkfTrackCandidatesMkFitSiStripHits",
        mkFitSeeds = "hltIter0IterL3MuonCkfTrackCandidatesMkFitSeeds",
        tracks = "hltIter0IterL3MuonCkfTrackCandidatesMkFit",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        propagatorAlong = ":PropagatorWithMaterialParabolicMf",
        propagatorOpposite = ":PropagatorWithMaterialParabolicMfOpposite",
    )

    process.HLTDoLocalStripSequence += process.hltSiStripRecHits

    replaceWith = (process.hltIter0IterL3MuonCkfTrackCandidatesMkFitSiPixelHits +
                   process.hltIter0IterL3MuonCkfTrackCandidatesMkFitSiStripHits +
                   process.hltIter0IterL3MuonCkfTrackCandidatesMkFitEventOfHits +
                   process.hltIter0IterL3MuonCkfTrackCandidatesMkFitSeeds +
                   process.hltIter0IterL3MuonCkfTrackCandidatesMkFit +
                   process.hltIter0IterL3MuonCkfTrackCandidates)

    process.HLTIterativeTrackingIteration0ForIterL3Muon.replace(process.hltIter0IterL3MuonCkfTrackCandidates, replaceWith)

    for path in process.paths_().values():
      if not path.contains(process.HLTIterativeTrackingIteration0ForIterL3Muon) and path.contains(process.hltIter0IterL3MuonCkfTrackCandidates):
        path.replace(process.hltIter0IterL3MuonCkfTrackCandidates, replaceWith)

    # process.hltIter0IterL3MuonCkfTrackCandidatesMkFitConfig.config = 'RecoTracker/MkFit/data/mkfit-phase1-hltiter0.json'

    # process.hltIter0IterL3MuonTrackCutClassifier.mva.maxChi2 = cms.vdouble( 999.0, 25.0, 99.0 )

    # process.hltIter0IterL3MuonTrackCutClassifier.mva.maxChi2n = cms.vdouble( 1.2, 1.0, 999.0 )

    #process.hltIter0IterL3MuonTrackCutClassifier.mva.dr_par = cms.PSet( 
    #    d0err = cms.vdouble( 0.003, 0.003, 0.003 ),
    #    dr_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
    #    dr_par2 = cms.vdouble( 3.40282346639E38, 0.45, 0.45 ),
    #    dr_exp = cms.vint32( 4, 4, 4 ),
    #    d0err_par = cms.vdouble( 0.001, 0.001, 0.001 )
    #)
    #process.hltIter0IterL3MuonTrackCutClassifier.mva.dz_par = cms.PSet( 
    #    dz_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
    #    dz_par2 = cms.vdouble( 3.40282346639E38, 0.51, 0.51 ),
    #    dz_exp = cms.vint32( 4, 4, 4 )
    #)

    return process

        
def customizeHLTIter0ForIterL3FromL1MuonToMkFit(process):
    for objLabel in [
            'hltSiStripRawToClustersFacility',
            'HLTDoLocalStripSequence',
            'HLTIterativeTrackingIteration0ForIterL3FromL1Muon',
            'hltIter0IterL3FromL1MuonCkfTrackCandidates',
    ]:
        if not hasattr(process, objLabel):
            print(f'# WARNING: customizeHLTIter0ForIterL3FromL1MuonToMkFit failed (object with label "{objLabel}" not found) - no customisation applied !')
            return process

    # mkFit needs all clusters, so switch off the on-demand mode
    process.hltSiStripRawToClustersFacility = cms.EDProducer(
        "SiStripClusterizerFromRaw",
        ProductLabel = cms.InputTag( "rawDataCollector" ),
        ConditionsLabel = cms.string( "" ),
        onDemand = cms.bool( True ),
        DoAPVEmulatorCheck = cms.bool( False ),
        LegacyUnpacker = cms.bool( False ),
        HybridZeroSuppressed = cms.bool( False ),
        Clusterizer = cms.PSet( 
            ConditionsLabel = cms.string( "" ),
            MaxClusterSize = cms.uint32( 32 ), 
            ClusterThreshold = cms.double( 5.0 ),
            SeedThreshold = cms.double( 3.0 ),
            Algorithm = cms.string( "ThreeThresholdAlgorithm" ),
            ChannelThreshold = cms.double( 2.0 ),
            MaxAdjacentBad = cms.uint32( 0 ),
            setDetId = cms.bool( True ),
            MaxSequentialHoles = cms.uint32( 0 ),
            RemoveApvShots = cms.bool( True ),
            clusterChargeCut = cms.PSet(  refToPSet_ = cms.string( "HLTSiStripClusterChargeCutNone" ) ),
            MaxSequentialBad = cms.uint32( 1 )
        ),
        Algorithms = cms.PSet( 
            Use10bitsTruncation = cms.bool( False ),
            CommonModeNoiseSubtractionMode = cms.string( "Median" ),
            useCMMeanMap = cms.bool( False ),
            TruncateInSuppressor = cms.bool( True ),
            doAPVRestore = cms.bool( False ),
            SiStripFedZeroSuppressionMode = cms.uint32( 4 ),
            PedestalSubtractionFedMode = cms.bool( True )
        )
    )
    process.hltSiStripRawToClustersFacility.onDemand = False
    process.hltSiStripRawToClustersFacility.Clusterizer.MaxClusterSize = 8

    process.hltSiStripRecHits = SiStripRecHitConverter_cfi.siStripMatchedRecHits.clone(
        ClusterProducer = "hltSiStripRawToClustersFacility",
        StripCPE = "hltESPStripCPEfromTrackAngle:hltESPStripCPEfromTrackAngle",
        doMatching = False,
    )

    # Use fourth hit if one is available
    process.hltIter0IterL3FromL1MuonPixelSeedsFromPixelTracks.includeFourthHit = cms.bool(True)

    process.load("RecoTracker.MkFit.mkFitGeometryESProducer_cfi")

    process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiPixelHits = mkFitSiPixelHitConverter_cfi.mkFitSiPixelHitConverter.clone(
        hits = "hltSiPixelRecHits",
        clusters = "hltSiPixelClusters",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiStripHits = mkFitSiStripHitConverter_cfi.mkFitSiStripHitConverter.clone(
        rphiHits = "hltSiStripRecHits:rphiRecHit",
        stereoHits = "hltSiStripRecHits:stereoRecHit",
        clusters = "hltSiStripRawToClustersFacility",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutLoose'),
    )
    process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitEventOfHits = mkFitEventOfHitsProducer_cfi.mkFitEventOfHitsProducer.clone(
        beamSpot  = "hltOnlineBeamSpot",
        pixelHits = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiStripHits",
    )
    process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSeeds = mkFitSeedConverter_cfi.mkFitSeedConverter.clone(
        seeds = "hltIter0IterL3FromL1MuonPixelSeedsFromPixelTracksFiltered",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0IterL3FromL1MuonTrackCandidatesMkFitConfig = mkFitIterationConfigESProducer_cfi.mkFitIterationConfigESProducer.clone(
        ComponentName = 'hltIter0IterL3FromL1MuonTrackCandidatesMkFitConfig',
        config = 'RecoTracker/MkFit/data/mkfit-phase1-initialStep.json',
    )
    process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFit = mkFitProducer_cfi.mkFitProducer.clone(
        pixelHits = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiStripHits",
        eventOfHits = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitEventOfHits",
        seeds = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSeeds",
        config = ('', 'hltIter0IterL3FromL1MuonTrackCandidatesMkFitConfig'),
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutNone'),
    )
    process.hltIter0IterL3FromL1MuonCkfTrackCandidates = mkFitOutputConverter_cfi.mkFitOutputConverter.clone(
        seeds = "hltIter0IterL3FromL1MuonPixelSeedsFromPixelTracksFiltered",
        mkFitEventOfHits = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitEventOfHits",
        mkFitPixelHits = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiPixelHits",
        mkFitStripHits = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiStripHits",
        mkFitSeeds = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSeeds",
        tracks = "hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFit",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        propagatorAlong = ":PropagatorWithMaterialParabolicMf",
        propagatorOpposite = ":PropagatorWithMaterialParabolicMfOpposite",
    )

    process.HLTDoLocalStripSequence += process.hltSiStripRecHits

    replaceWith = (process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiPixelHits +
                   process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSiStripHits +
                   process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitEventOfHits +
                   process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFitSeeds +
                   process.hltIter0IterL3FromL1MuonCkfTrackCandidatesMkFit +
                   process.hltIter0IterL3FromL1MuonCkfTrackCandidates)

    process.HLTIterativeTrackingIteration0ForIterL3FromL1Muon.replace(process.hltIter0IterL3FromL1MuonCkfTrackCandidates, replaceWith)

    for path in process.paths_().values():
      if not path.contains(process.HLTIterativeTrackingIteration0ForIterL3FromL1Muon) and path.contains(process.hltIter0IterL3FromL1MuonCkfTrackCandidates):
        path.replace(process.hltIter0IterL3FromL1MuonCkfTrackCandidates, replaceWith)

    process.hltIter0IterL3FromL1MuonTrackCandidatesMkFitConfig.config = 'RecoTracker/MkFit/data/mkfit-phase1-hltiter0.json'

    # process.hltIter0IterL3FromL1MuonTrackCutClassifier.mva.maxChi2 = cms.vdouble( 999.0, 25.0, 99.0 )

    # process.hltIter0IterL3FromL1MuonTrackCutClassifier.mva.maxChi2n = cms.vdouble( 1.2, 1.0, 999.0 )

    #process.hltIter0IterL3FromL1MuonTrackCutClassifier.mva.dr_par = cms.PSet( 
    #    d0err = cms.vdouble( 0.003, 0.003, 0.003 ),
    #    dr_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
    #    dr_par2 = cms.vdouble( 3.40282346639E38, 0.45, 0.45 ),
    #    dr_exp = cms.vint32( 4, 4, 4 ),
    #    d0err_par = cms.vdouble( 0.001, 0.001, 0.001 )
    #)
    #process.hltIter0IterL3FromL1MuonTrackCutClassifier.mva.dz_par = cms.PSet( 
    #    dz_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
    #    dz_par2 = cms.vdouble( 3.40282346639E38, 0.51, 0.51 ),
    #    dz_exp = cms.vint32( 4, 4, 4 )
    #)

    return process
    
def customizeIterTrackL3MuonIter0_forMuonIso(process):

    for objLabel in [
            'hltSiStripRawToClustersFacility',
            'HLTDoLocalStripSequence',
            'HLTIterativeTrackingL3MuonIteration0',
            'hltIter0L3MuonCkfTrackCandidates',
    ]:
        if not hasattr(process, objLabel):
            print(f'# WARNING: customizeIterTrackL3MuonIter0_forMuonIso failed (object with label "{objLabel}" not found) - no customisation applied !')
            return process

    # mkFit needs all clusters, so switch off the on-demand mode
    process.hltSiStripRawToClustersFacility = cms.EDProducer(
        "SiStripClusterizerFromRaw",
        ProductLabel = cms.InputTag( "rawDataCollector" ),
        ConditionsLabel = cms.string( "" ),
        onDemand = cms.bool( True ),
        DoAPVEmulatorCheck = cms.bool( False ),
        LegacyUnpacker = cms.bool( False ),
        HybridZeroSuppressed = cms.bool( False ),
        Clusterizer = cms.PSet( 
            ConditionsLabel = cms.string( "" ),
            MaxClusterSize = cms.uint32( 32 ), 
            ClusterThreshold = cms.double( 5.0 ),
            SeedThreshold = cms.double( 3.0 ),
            Algorithm = cms.string( "ThreeThresholdAlgorithm" ),
            ChannelThreshold = cms.double( 2.0 ),
            MaxAdjacentBad = cms.uint32( 0 ),
            setDetId = cms.bool( True ),
            MaxSequentialHoles = cms.uint32( 0 ),
            RemoveApvShots = cms.bool( True ),
            clusterChargeCut = cms.PSet(  refToPSet_ = cms.string( "HLTSiStripClusterChargeCutNone" ) ),
            MaxSequentialBad = cms.uint32( 1 )
        ),
        Algorithms = cms.PSet( 
            Use10bitsTruncation = cms.bool( False ),
            CommonModeNoiseSubtractionMode = cms.string( "Median" ),
            useCMMeanMap = cms.bool( False ),
            TruncateInSuppressor = cms.bool( True ),
            doAPVRestore = cms.bool( False ),
            SiStripFedZeroSuppressionMode = cms.uint32( 4 ),
            PedestalSubtractionFedMode = cms.bool( True )
        )
    )
    process.hltSiStripRawToClustersFacility.onDemand = False
    process.hltSiStripRawToClustersFacility.Clusterizer.MaxClusterSize = 8

    process.hltSiStripRecHits = SiStripRecHitConverter_cfi.siStripMatchedRecHits.clone(
        ClusterProducer = "hltSiStripRawToClustersFacility",
        StripCPE = "hltESPStripCPEfromTrackAngle:hltESPStripCPEfromTrackAngle",
        doMatching = False,
    )

    # Use fourth hit if one is available
    process.hltIter0L3MuonPixelSeedsFromPixelTracks.includeFourthHit = cms.bool(True)

    process.load("RecoTracker.MkFit.mkFitGeometryESProducer_cfi")

    process.hltIter0L3MuonCkfTrackCandidatesMkFitSiPixelHits = mkFitSiPixelHitConverter_cfi.mkFitSiPixelHitConverter.clone(
        hits = "hltSiPixelRecHits",
        clusters = "hltSiPixelClusters",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0L3MuonCkfTrackCandidatesMkFitSiStripHits = mkFitSiStripHitConverter_cfi.mkFitSiStripHitConverter.clone(
        rphiHits = "hltSiStripRecHits:rphiRecHit",
        stereoHits = "hltSiStripRecHits:stereoRecHit",
        clusters = "hltSiStripRawToClustersFacility",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutLoose'),
    )
    process.hltIter0L3MuonCkfTrackCandidatesMkFitEventOfHits = mkFitEventOfHitsProducer_cfi.mkFitEventOfHitsProducer.clone(
        beamSpot  = "hltOnlineBeamSpot",
        pixelHits = "hltIter0L3MuonCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0L3MuonCkfTrackCandidatesMkFitSiStripHits",
    )
    process.hltIter0L3MuonCkfTrackCandidatesMkFitSeeds = mkFitSeedConverter_cfi.mkFitSeedConverter.clone(
        seeds = "hltIter0L3MuonPixelSeedsFromPixelTracks",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0L3MuonTrackCandidatesMkFitConfig = mkFitIterationConfigESProducer_cfi.mkFitIterationConfigESProducer.clone(
        ComponentName = 'hltIter0L3MuonTrackCandidatesMkFitConfig',
        config = 'RecoTracker/MkFit/data/mkfit-phase1-initialStep.json',
    )
    process.hltIter0L3MuonCkfTrackCandidatesMkFit = mkFitProducer_cfi.mkFitProducer.clone(
        pixelHits = "hltIter0L3MuonCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0L3MuonCkfTrackCandidatesMkFitSiStripHits",
        eventOfHits = "hltIter0L3MuonCkfTrackCandidatesMkFitEventOfHits",
        seeds = "hltIter0L3MuonCkfTrackCandidatesMkFitSeeds",
        config = ('', 'hltIter0L3MuonTrackCandidatesMkFitConfig'),
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutNone'),
    )
    process.hltIter0L3MuonCkfTrackCandidates = mkFitOutputConverter_cfi.mkFitOutputConverter.clone(
        seeds = "hltIter0L3MuonPixelSeedsFromPixelTracks",
        mkFitEventOfHits = "hltIter0L3MuonCkfTrackCandidatesMkFitEventOfHits",
        mkFitPixelHits = "hltIter0L3MuonCkfTrackCandidatesMkFitSiPixelHits",
        mkFitStripHits = "hltIter0L3MuonCkfTrackCandidatesMkFitSiStripHits",
        mkFitSeeds = "hltIter0L3MuonCkfTrackCandidatesMkFitSeeds",
        tracks = "hltIter0L3MuonCkfTrackCandidatesMkFit",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        propagatorAlong = ":PropagatorWithMaterialParabolicMf",
        propagatorOpposite = ":PropagatorWithMaterialParabolicMfOpposite",
    )

    process.HLTDoLocalStripSequence += process.hltSiStripRecHits

    replaceWith = (process.hltIter0L3MuonCkfTrackCandidatesMkFitSiPixelHits +
                   process.hltIter0L3MuonCkfTrackCandidatesMkFitSiStripHits +
                   process.hltIter0L3MuonCkfTrackCandidatesMkFitEventOfHits +
                   process.hltIter0L3MuonCkfTrackCandidatesMkFitSeeds +
                   process.hltIter0L3MuonCkfTrackCandidatesMkFit +
                   process.hltIter0L3MuonCkfTrackCandidates)

    process.HLTIterativeTrackingL3MuonIteration0.replace(process.hltIter0L3MuonCkfTrackCandidates, replaceWith)

    for path in process.paths_().values():
      if not path.contains(process.HLTIterativeTrackingL3MuonIteration0) and path.contains(process.hltIter0L3MuonCkfTrackCandidates):
        path.replace(process.hltIter0L3MuonCkfTrackCandidates, replaceWith)

    process.hltIter0L3MuonTrackCandidatesMkFitConfig.config = 'RecoTracker/MkFit/data/mkfit-phase1-hltiter0.json'

    process.hltIter0L3MuonTrackCutClassifier.mva.maxChi2 = cms.vdouble( 999.0, 25.0, 99.0 )

    process.hltIter0L3MuonTrackCutClassifier.mva.maxChi2n = cms.vdouble( 1.2, 1.0, 999.0 )

    process.hltIter0L3MuonTrackCutClassifier.mva.dr_par = cms.PSet( 
        d0err = cms.vdouble( 0.003, 0.003, 0.003 ),
        dr_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
        dr_par2 = cms.vdouble( 3.40282346639E38, 0.45, 0.45 ),
        dr_exp = cms.vint32( 4, 4, 4 ),
        d0err_par = cms.vdouble( 0.001, 0.001, 0.001 )
    )
    process.hltIter0L3MuonTrackCutClassifier.mva.dz_par = cms.PSet( 
        dz_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
        dz_par2 = cms.vdouble( 3.40282346639E38, 0.51, 0.51 ),
        dz_exp = cms.vint32( 4, 4, 4 )
    )

    return process

def customizeHLTIter0HighPtTkMuToMkFit(process):
    # if any of the following objects does not exist, do not apply any customisation
    for objLabel in [
            'hltSiStripRawToClustersFacility',
            'HLTDoLocalStripSequence',
            'HLTIterativeTrackingHighPtTkMuIteration0',
            'hltIter0HighPtTkMuCkfTrackCandidates',
    ]:
        if not hasattr(process, objLabel):
            print(f'# WARNING: customizeHLTIter0HighPtTkMuToMkFit failed (object with label "{objLabel}" not found) - no customisation applied !')
            return process

    process.hltSiStripRawToClustersFacility = cms.EDProducer(
        "SiStripClusterizerFromRaw",
        ProductLabel = cms.InputTag( "rawDataCollector" ),
        ConditionsLabel = cms.string( "" ),
        onDemand = cms.bool( True ),
        DoAPVEmulatorCheck = cms.bool( False ),
        LegacyUnpacker = cms.bool( False ),
        HybridZeroSuppressed = cms.bool( False ),
        Clusterizer = cms.PSet(
            ConditionsLabel = cms.string( "" ),
            MaxClusterSize = cms.uint32( 32 ),
            ClusterThreshold = cms.double( 5.0 ),
            SeedThreshold = cms.double( 3.0 ),
            Algorithm = cms.string( "ThreeThresholdAlgorithm" ),
            ChannelThreshold = cms.double( 2.0 ),
            MaxAdjacentBad = cms.uint32( 0 ),
            setDetId = cms.bool( True ),
            MaxSequentialHoles = cms.uint32( 0 ),
            RemoveApvShots = cms.bool( True ),
            clusterChargeCut = cms.PSet(  refToPSet_ = cms.string( "HLTSiStripClusterChargeCutNone" ) ),
            MaxSequentialBad = cms.uint32( 1 )
        ),
        Algorithms = cms.PSet(
            Use10bitsTruncation = cms.bool( False ),
            CommonModeNoiseSubtractionMode = cms.string( "Median" ),
            useCMMeanMap = cms.bool( False ),
            TruncateInSuppressor = cms.bool( True ),
            doAPVRestore = cms.bool( False ),
            SiStripFedZeroSuppressionMode = cms.uint32( 4 ),
            PedestalSubtractionFedMode = cms.bool( True )
        )
    )
    process.hltSiStripRawToClustersFacility.onDemand = False
    process.hltSiStripRawToClustersFacility.Clusterizer.MaxClusterSize = 8

    process.hltSiStripRecHits = SiStripRecHitConverter_cfi.siStripMatchedRecHits.clone(
        ClusterProducer = "hltSiStripRawToClustersFacility",
        StripCPE = "hltESPStripCPEfromTrackAngle:hltESPStripCPEfromTrackAngle",
        doMatching = False,
    )

    # Use fourth hit if one is available
    process.hltIter0HighPtTkMuPixelSeedsFromPixelTracks.includeFourthHit = cms.bool(True)

    process.load("RecoTracker.MkFit.mkFitGeometryESProducer_cfi")

    process.hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiPixelHits = mkFitSiPixelHitConverter_cfi.mkFitSiPixelHitConverter.clone(
        hits = "hltSiPixelRecHits",
        clusters = "hltSiPixelClusters",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiStripHits = mkFitSiStripHitConverter_cfi.mkFitSiStripHitConverter.clone(
        rphiHits = "hltSiStripRecHits:rphiRecHit",
        stereoHits = "hltSiStripRecHits:stereoRecHit",
        clusters = "hltSiStripRawToClustersFacility",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutLoose'),
    )
    process.hltIter0HighPtTkMuCkfTrackCandidatesMkFitEventOfHits = mkFitEventOfHitsProducer_cfi.mkFitEventOfHitsProducer.clone(
        beamSpot  = "hltOnlineBeamSpot",
        pixelHits = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiStripHits",
    )
    process.hltIter0HighPtTkMuCkfTrackCandidatesMkFitSeeds = mkFitSeedConverter_cfi.mkFitSeedConverter.clone(
        seeds = "hltIter0HighPtTkMuPixelSeedsFromPixelTracks",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0HighPtTkMuTrackCandidatesMkFitConfig = mkFitIterationConfigESProducer_cfi.mkFitIterationConfigESProducer.clone(
        ComponentName = 'hltIter0HighPtTkMuTrackCandidatesMkFitConfig',
        config = 'RecoTracker/MkFit/data/mkfit-phase1-initialStep.json',
    )
    process.hltIter0HighPtTkMuCkfTrackCandidatesMkFit = mkFitProducer_cfi.mkFitProducer.clone(
        pixelHits = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiStripHits",
        eventOfHits = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitEventOfHits",
        seeds = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitSeeds",
        config = ('', 'hltIter0HighPtTkMuTrackCandidatesMkFitConfig'),
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutNone'),
    )
    process.hltIter0HighPtTkMuCkfTrackCandidates = mkFitOutputConverter_cfi.mkFitOutputConverter.clone(
        seeds = "hltIter0HighPtTkMuPixelSeedsFromPixelTracks",
        mkFitEventOfHits = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitEventOfHits",
        mkFitPixelHits = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiPixelHits",
        mkFitStripHits = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiStripHits",
        mkFitSeeds = "hltIter0HighPtTkMuCkfTrackCandidatesMkFitSeeds",
        tracks = "hltIter0HighPtTkMuCkfTrackCandidatesMkFit",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        propagatorAlong = ":PropagatorWithMaterialParabolicMf",
        propagatorOpposite = ":PropagatorWithMaterialParabolicMfOpposite",
    )

    process.HLTDoLocalStripSequence += process.hltSiStripRecHits

    replaceWith = (process.hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiPixelHits +
                   process.hltIter0HighPtTkMuCkfTrackCandidatesMkFitSiStripHits +
                   process.hltIter0HighPtTkMuCkfTrackCandidatesMkFitEventOfHits +
                   process.hltIter0HighPtTkMuCkfTrackCandidatesMkFitSeeds +
                   process.hltIter0HighPtTkMuCkfTrackCandidatesMkFit +
                   process.hltIter0HighPtTkMuCkfTrackCandidates)

    process.HLTIterativeTrackingHighPtTkMuIteration0.replace(process.hltIter0HighPtTkMuCkfTrackCandidates, replaceWith)

    for path in process.paths_().values():
      if not path.contains(process.HLTIterativeTrackingHighPtTkMuIteration0) and path.contains(process.hltIter0HighPtTkMuCkfTrackCandidates):
        path.replace(process.hltIter0HighPtTkMuCkfTrackCandidates, replaceWith)

    process.hltIter0HighPtTkMuTrackCandidatesMkFitConfig.config = 'RecoTracker/MkFit/data/mkfit-phase1-hltiter0.json'

    return process


    
def customizeHLTIter0ToMkFit(process):

    # if any of the following objects does not exist, do not apply any customisation
    for objLabel in [
        'hltSiStripRawToClustersFacility',
        'HLTDoLocalStripSequence',
        'HLTIterativeTrackingIteration0',
        'hltIter0PFlowCkfTrackCandidates',
    ]:
        if not hasattr(process, objLabel):
            print(f'# WARNING: customizeHLTIter0ToMkFit failed (object with label "{objLabel}" not found) - no customisation applied !')
            return process

    # mkFit needs all clusters, so switch off the on-demand mode
    process.hltSiStripRawToClustersFacility = cms.EDProducer(
        "SiStripClusterizerFromRaw",
        ProductLabel = cms.InputTag( "rawDataCollector" ),
        ConditionsLabel = cms.string( "" ),
        onDemand = cms.bool( True ),
        DoAPVEmulatorCheck = cms.bool( False ),
        LegacyUnpacker = cms.bool( False ),
        HybridZeroSuppressed = cms.bool( False ),
        Clusterizer = cms.PSet( 
            ConditionsLabel = cms.string( "" ),
            MaxClusterSize = cms.uint32( 32 ), 
            ClusterThreshold = cms.double( 5.0 ),
            SeedThreshold = cms.double( 3.0 ),
            Algorithm = cms.string( "ThreeThresholdAlgorithm" ),
            ChannelThreshold = cms.double( 2.0 ),
            MaxAdjacentBad = cms.uint32( 0 ),
            setDetId = cms.bool( True ),
            MaxSequentialHoles = cms.uint32( 0 ),
            RemoveApvShots = cms.bool( True ),
            clusterChargeCut = cms.PSet(  refToPSet_ = cms.string( "HLTSiStripClusterChargeCutNone" ) ),
            MaxSequentialBad = cms.uint32( 1 )
        ),
        Algorithms = cms.PSet( 
            Use10bitsTruncation = cms.bool( False ),
            CommonModeNoiseSubtractionMode = cms.string( "Median" ),
            useCMMeanMap = cms.bool( False ),
            TruncateInSuppressor = cms.bool( True ),
            doAPVRestore = cms.bool( False ),
            SiStripFedZeroSuppressionMode = cms.uint32( 4 ),
            PedestalSubtractionFedMode = cms.bool( True )
        )
    )
    process.hltSiStripRawToClustersFacility.onDemand = False
    process.hltSiStripRawToClustersFacility.Clusterizer.MaxClusterSize = 8

    process.hltSiStripRecHits = SiStripRecHitConverter_cfi.siStripMatchedRecHits.clone(
        ClusterProducer = "hltSiStripRawToClustersFacility",
        StripCPE = "hltESPStripCPEfromTrackAngle:hltESPStripCPEfromTrackAngle",
        doMatching = False,
    )

    # Use fourth hit if one is available
    process.hltIter0PFLowPixelSeedsFromPixelTracks.includeFourthHit = cms.bool(True)

    process.load("RecoTracker.MkFit.mkFitGeometryESProducer_cfi")

    process.hltIter0PFlowCkfTrackCandidatesMkFitSiPixelHits = mkFitSiPixelHitConverter_cfi.mkFitSiPixelHitConverter.clone(
        hits = "hltSiPixelRecHits",
        clusters = "hltSiPixelClusters",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0PFlowCkfTrackCandidatesMkFitSiStripHits = mkFitSiStripHitConverter_cfi.mkFitSiStripHitConverter.clone(
        rphiHits = "hltSiStripRecHits:rphiRecHit",
        stereoHits = "hltSiStripRecHits:stereoRecHit",
        clusters = "hltSiStripRawToClustersFacility",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutLoose'),
    )
    process.hltIter0PFlowCkfTrackCandidatesMkFitEventOfHits = mkFitEventOfHitsProducer_cfi.mkFitEventOfHitsProducer.clone(
        beamSpot  = "hltOnlineBeamSpot",
        pixelHits = "hltIter0PFlowCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0PFlowCkfTrackCandidatesMkFitSiStripHits",
    )
    process.hltIter0PFlowCkfTrackCandidatesMkFitSeeds = mkFitSeedConverter_cfi.mkFitSeedConverter.clone(
        seeds = "hltIter0PFLowPixelSeedsFromPixelTracks",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
    )
    process.hltIter0PFlowTrackCandidatesMkFitConfig = mkFitIterationConfigESProducer_cfi.mkFitIterationConfigESProducer.clone(
        ComponentName = 'hltIter0PFlowTrackCandidatesMkFitConfig',
        config = 'RecoTracker/MkFit/data/mkfit-phase1-initialStep.json',
    )
    process.hltIter0PFlowCkfTrackCandidatesMkFit = mkFitProducer_cfi.mkFitProducer.clone(
        pixelHits = "hltIter0PFlowCkfTrackCandidatesMkFitSiPixelHits",
        stripHits = "hltIter0PFlowCkfTrackCandidatesMkFitSiStripHits",
        eventOfHits = "hltIter0PFlowCkfTrackCandidatesMkFitEventOfHits",
        seeds = "hltIter0PFlowCkfTrackCandidatesMkFitSeeds",
        config = ('', 'hltIter0PFlowTrackCandidatesMkFitConfig'),
        minGoodStripCharge = dict(refToPSet_ = 'HLTSiStripClusterChargeCutNone'),
    )
    process.hltIter0PFlowCkfTrackCandidates = mkFitOutputConverter_cfi.mkFitOutputConverter.clone(
        seeds = "hltIter0PFLowPixelSeedsFromPixelTracks",
        mkFitEventOfHits = "hltIter0PFlowCkfTrackCandidatesMkFitEventOfHits",
        mkFitPixelHits = "hltIter0PFlowCkfTrackCandidatesMkFitSiPixelHits",
        mkFitStripHits = "hltIter0PFlowCkfTrackCandidatesMkFitSiStripHits",
        mkFitSeeds = "hltIter0PFlowCkfTrackCandidatesMkFitSeeds",
        tracks = "hltIter0PFlowCkfTrackCandidatesMkFit",
        ttrhBuilder = ":hltESPTTRHBWithTrackAngle",
        propagatorAlong = ":PropagatorWithMaterialParabolicMf",
        propagatorOpposite = ":PropagatorWithMaterialParabolicMfOpposite",
    )

    process.HLTDoLocalStripSequence += process.hltSiStripRecHits

    replaceWith = (process.hltIter0PFlowCkfTrackCandidatesMkFitSiPixelHits +
                   process.hltIter0PFlowCkfTrackCandidatesMkFitSiStripHits +
                   process.hltIter0PFlowCkfTrackCandidatesMkFitEventOfHits +
                   process.hltIter0PFlowCkfTrackCandidatesMkFitSeeds +
                   process.hltIter0PFlowCkfTrackCandidatesMkFit +
                   process.hltIter0PFlowCkfTrackCandidates)

    process.HLTIterativeTrackingIteration0.replace(process.hltIter0PFlowCkfTrackCandidates, replaceWith)

    for path in process.paths_().values():
      if not path.contains(process.HLTIterativeTrackingIteration0) and path.contains(process.hltIter0PFlowCkfTrackCandidates):
        path.replace(process.hltIter0PFlowCkfTrackCandidates, replaceWith)

    process.hltIter0PFlowTrackCandidatesMkFitConfig.config = 'RecoTracker/MkFit/data/mkfit-phase1-hltiter0.json'

    process.hltIter0PFlowTrackCutClassifier.mva.maxChi2 = cms.vdouble( 999.0, 25.0, 99.0 )

    process.hltIter0PFlowTrackCutClassifier.mva.maxChi2n = cms.vdouble( 1.2, 1.0, 999.0 )

    process.hltIter0PFlowTrackCutClassifier.mva.dr_par = cms.PSet( 
        d0err = cms.vdouble( 0.003, 0.003, 0.003 ),
        dr_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
        dr_par2 = cms.vdouble( 3.40282346639E38, 0.45, 0.45 ),
        dr_exp = cms.vint32( 4, 4, 4 ),
        d0err_par = cms.vdouble( 0.001, 0.001, 0.001 )
    )
    process.hltIter0PFlowTrackCutClassifier.mva.dz_par = cms.PSet( 
        dz_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
        dz_par2 = cms.vdouble( 3.40282346639E38, 0.51, 0.51 ),
        dz_exp = cms.vint32( 4, 4, 4 )
    )

    if hasattr(process, 'hltIter0PFlowTrackCutClassifierSerialSync'):
        process.hltIter0PFlowTrackCutClassifierSerialSync.mva.maxChi2 = cms.vdouble( 999.0, 25.0, 99.0 )
        process.hltIter0PFlowTrackCutClassifierSerialSync.mva.maxChi2n = cms.vdouble( 1.2, 1.0, 999.0 )
        process.hltIter0PFlowTrackCutClassifierSerialSync.mva.dr_par = cms.PSet( 
            d0err = cms.vdouble( 0.003, 0.003, 0.003 ),
            dr_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
            dr_par2 = cms.vdouble( 3.40282346639E38, 0.45, 0.45 ),
            dr_exp = cms.vint32( 4, 4, 4 ),
            d0err_par = cms.vdouble( 0.001, 0.001, 0.001 )
        )
        process.hltIter0PFlowTrackCutClassifierSerialSync.mva.dz_par = cms.PSet( 
            dz_par1 = cms.vdouble( 3.40282346639E38, 0.6, 0.6 ),
            dz_par2 = cms.vdouble( 3.40282346639E38, 0.51, 0.51 ),
            dz_exp = cms.vint32( 4, 4, 4 )
        )

    return process

def customizeHLTSiStripClusterizerOnDemandFalse(process):

    # if any of the following objects does not exist, do not apply any customisation
    for objLabel in [
        'hltSiStripRawToClustersFacility',
    ]:
        if not hasattr(process, objLabel):
            print(f'# WARNING: customize command failed (object with label "{objLabel}" not found) - no customisation applied !')
            return process

    # mkFit needs all clusters, so switch off the on-demand mode
    process.hltSiStripRawToClustersFacility.onDemand = False
    return process

def customizeHLTSiStripClusterizerOnDemandFalseMaxClusterSize8(process):

    for objLabel in [
        'hltSiStripRawToClustersFacility',
    ]:
        if not hasattr(process, objLabel):
            print(f'# WARNING: customize command failed (object with label "{objLabel}" not found) - no customisation applied !')
            return process

    process.hltSiStripRawToClustersFacility = cms.EDProducer(
        "SiStripClusterizerFromRaw",
        ProductLabel = cms.InputTag( "rawDataCollector" ),
        ConditionsLabel = cms.string( "" ),
        onDemand = cms.bool( True ),
        DoAPVEmulatorCheck = cms.bool( False ),
        LegacyUnpacker = cms.bool( False ),
        HybridZeroSuppressed = cms.bool( False ),
        Clusterizer = cms.PSet( 
            ConditionsLabel = cms.string( "" ),
            MaxClusterSize = cms.uint32( 32 ), 
            ClusterThreshold = cms.double( 5.0 ),
            SeedThreshold = cms.double( 3.0 ),
            Algorithm = cms.string( "ThreeThresholdAlgorithm" ),
            ChannelThreshold = cms.double( 2.0 ),
            MaxAdjacentBad = cms.uint32( 0 ),
            setDetId = cms.bool( True ),
            MaxSequentialHoles = cms.uint32( 0 ),
            RemoveApvShots = cms.bool( True ),
            clusterChargeCut = cms.PSet(  refToPSet_ = cms.string( "HLTSiStripClusterChargeCutNone" ) ),
            MaxSequentialBad = cms.uint32( 1 )
        ),
        Algorithms = cms.PSet( 
            Use10bitsTruncation = cms.bool( False ),
            CommonModeNoiseSubtractionMode = cms.string( "Median" ),
            useCMMeanMap = cms.bool( False ),
            TruncateInSuppressor = cms.bool( True ),
            doAPVRestore = cms.bool( False ),
            SiStripFedZeroSuppressionMode = cms.uint32( 4 ),
            PedestalSubtractionFedMode = cms.bool( True )
        )
    )
    process.hltSiStripRawToClustersFacility.onDemand = False
    process.hltSiStripRawToClustersFacility.Clusterizer.MaxClusterSize = 8

    return process

def modifyMinOutputModuleForTrackingValidation(process, filename="output.root"):

    for objLabel in [
        'hltOutputMinimal',
    ]:
        if not hasattr(process, objLabel):
            print(f'# WARNING: customize command failed (object with label "{objLabel}" not found) - no customisation applied !')
            return process

    process.hltOutputMinimal.outputCommands = cms.untracked.vstring(
        'drop *',
        'keep edmTriggerResults_*_*_*',
        'keep triggerTriggerEvent_*_*_*',
        'keep GlobalAlgBlkBXVector_*_*_*',
        'keep GlobalExtBlkBXVector_*_*_*',
        'keep l1tEGammaBXVector_*_EGamma_*',
        'keep l1tEtSumBXVector_*_EtSum_*',
        'keep l1tJetBXVector_*_Jet_*',
        'keep l1tMuonBXVector_*_Muon_*',
        'keep l1tTauBXVector_*_Tau_*',
        'keep *_*_*_HLTX',
        'drop *_hltHbherecoLegacy_*_*',
        'drop *_hlt*Pixel*SoA*_*_*',
        'keep recoGenParticles_genParticles_*_*',
        'keep TrackingParticles_*_*_*',
        'keep *_*_MergedTrackTruth_*',
        'keep *_simSiPixelDigis_*_*',
        'keep *_simSiStripDigis_*_*',
        'keep PSimHits_g4SimHits_*_*',
        'keep SimTracks_g4SimHits_*_*',
        'keep SimVertexs_g4SimHits_*_*',
        'keep PileupSummaryInfos_addPileupInfo_*_*',
    )
    process.hltOutputMinimal.fileName = filename
    process.schedule.remove( process.DQMOutput )
    return process
