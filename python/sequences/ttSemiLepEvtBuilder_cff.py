import FWCore.ParameterSet.Config as cms


################################################################################
# produce ttSemiLepEvent structure with all necessary ingredients
################################################################################

## std sequence to produce the ttSemiLepEventHypotheses
from TopQuarkAnalysis.TopEventProducers.sequences.ttSemiLepEvtHypotheses_cff import *

## configure ttSemiLepEventBuilder
from TopQuarkAnalysis.TopEventProducers.producers.TtSemiLepEvtBuilder_cfi import *

## make ttSemiLepEvent
makeTtSemiLepEventBase = cms.Sequence(makeTtSemiLepHypotheses *
                                  ttSemiLepEvent
                                  )
makeTtSemiLepEvent = cms.Sequence(makeTtSemiLepEventBase)

################################################################################
## helper functions
## (examples of usage can be found in the ttSemiLepEvtBuilder_cfg.py)
################################################################################

## add hypotheses to the process
def addTtSemiLepHypotheses(process,
                           names
                           ):

    ## edit list of input hypotheses for the TtSemiLepEventBuilder
    labels =  getattr(process.ttSemiLepEvent, "hypotheses")
    for obj in names:
        ## create correct label from HypoClassKey string (stripping the leading "k")
        ## e.g. kKinFit -> ttSemiLepHypKinFit
        label = "ttSemiLepHyp" + obj[1:]
        ## add it to the list
        labels.append(label)
    process.ttSemiLepEvent.hypotheses = labels

    ## include hypotheses in the standard sequence
    sequence = getattr(process, "makeTtSemiLepHypotheses")
    for obj in names:
        ## create correct label from HypoClassKey string (stripping the leading "k")
        ## e.g. kKinFit -> makeHypothesis_kinFit
        if obj[1:4] == "MVA":
            label = "makeHypothesis_" + obj[1:4].lower() + obj[4:]
        else:
            label = "makeHypothesis_" + obj[1:2].lower() + obj[2:]
        ## add it to the sequence
        sequence += getattr(process, label)


## clone ttSemiLepEvent
def cloneTtSemiLepEvent(process
                        ):

    ## search highest already existing clone of ttSemiLepEvent
    ## to get the needed index for the new ttSemiLepEvent
    i=2
    while ("ttSemiLepEvent"+str(i) in process.producerNames()):
        i = i+1
    ## clone the ttSemiLepEvent including all hypotheses
    from PhysicsTools.PatAlgos.tools.helpers import cloneProcessingSnippet
    process.makeTtSemiLepEvent += cloneProcessingSnippet(process, process.makeTtSemiLepEventBase, str(i))

## remove genMatch hypothesis from the process
def removeTtSemiLepHypGenMatch(process):
    process.makeTtSemiLepHypotheses.remove(process.makeHypothesis_genMatch)
    process.ttSemiLepEvent.hypotheses.remove("ttSemiLepHypGenMatch")
    ## remove genMatch hypothesis for all clones of the ttSemiLepEvent
    i=2
    while ("ttSemiLepEvent"+str(i) in process.producerNames()):
       getattr(process, "makeTtSemiLepHypotheses"+str(i)).remove(getattr(process, "makeHypothesis_genMatch"+str(i)))
       getattr(process, "ttSemiLepEvent"+str(i)).hypotheses.remove(cms.InputTag("ttSemiLepHypGenMatch"+str(i)))
       ## remove full ttSemiLepEvent sequence if
       ## kGenMatch was the only included hypothesis
       if len(getattr(process, "ttSemiLepEvent"+str(i)).hypotheses) == 0:
           process.makeTtSemiLepEvent.remove(getattr(process,'makeTtSemiLepEventBase'+str(i)))
       i = i+1


## set a specific attribute for all hypotheses to a given value
## -> this works for "jets", "leps", "mets", "maxNJets"
def setForAllTtSemiLepHypotheses(process, attribute, value):
    modules = ["findTtSemiLepJetCombGeom",
               "findTtSemiLepJetCombMaxSumPtWMass",
               "findTtSemiLepJetCombMVA",
               "findTtSemiLepJetCombWMassDeltaTopMass",
               "findTtSemiLepJetCombWMassMaxSumPt",
               "hitFitTtSemiLepEventHypothesis",
               "kinFitTtSemiLepEventHypothesis",
               "ttSemiLepJetPartonMatch",
               "ttSemiLepHypGenMatch",
               "ttSemiLepHypGeom",
               "ttSemiLepHypHitFit",
               "ttSemiLepHypKinFit",
               "ttSemiLepHypMaxSumPtWMass",
               "ttSemiLepHypMVADisc",               
               "ttSemiLepHypWMassDeltaTopMass",
               "ttSemiLepHypWMassMaxSumPt"
               ]
    for obj in modules:
        object = getattr(process, obj)
        if hasattr(object, attribute):
            setattr(object, attribute, value)

## use electrons instead of muons for the hypotheses
def useElectronsForAllTtSemiLepHypotheses(process, elecLabel = "selectedPatElectrons"):
    ## use correct KinFitter module
    import TopQuarkAnalysis.TopKinFitter.TtSemiLepKinFitProducer_Electrons_cfi
    process.kinFitTtSemiLepEventHypothesis = TopQuarkAnalysis.TopKinFitter.TtSemiLepKinFitProducer_Electrons_cfi.kinFitTtSemiLepEvent.clone()
    import TopQuarkAnalysis.TopHitFit.TtSemiLepHitFitProducer_Electrons_cfi
    process.hitFitTtSemiLepEventHypothesis = TopQuarkAnalysis.TopHitFit.TtSemiLepHitFitProducer_Electrons_cfi.hitFitTtSemiLepEvent.clone()
    ## replace lepton InputTags in all modules
    setForAllTtSemiLepHypotheses(process, "leps", elecLabel)
