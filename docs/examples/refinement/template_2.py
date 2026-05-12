import json
import sys

import numpy as np
from scipy.optimize import least_squares

from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)
from diffpy.srfit.pdf import PDFGenerator, PDFParser
from diffpy.srfit.structure import constrainAsSpaceGroup
from diffpy.structure.parsers import getParser

# from diffpy.srfit.pdf.characteristicfunctions import sphericalCF

PDF_RMIN = 1.5
PDF_RMAX = 50
PDF_RSTEP = 0.01
QMAX = 25
QMIN = 0.1
DELTA2_I = 2
QDAMP_I = 0.04
QBROAD_I = 0.02
RUN_PARALLEL = True


def main(json_file):
    with open(json_file, "r") as f:
        kwargs = json.load(f)
    print(f"Running refinement with input args: {kwargs}")
    profile = Profile()
    parser = PDFParser()
    parser.parseFile(kwargs["profile"])
    profile.loadParsedData(parser)
    profile.setCalculationRange(xmin=PDF_RMIN, xmax=PDF_RMAX, dx=PDF_RSTEP)
    generators = []
    spacegroups = []
    phase_names = []
    contribution = FitContribution("pdfcontribution")
    for phase_name, cif_path in kwargs["structures"].items():
        p_cif = getParser("cif")
        stru1 = p_cif.parseFile(cif_path)
        sg = p_cif.spacegroup.short_name
        pdfgenerator = PDFGenerator(phase_name)
        pdfgenerator.setStructure(stru1, periodic=True)
        contribution.addProfileGenerator(pdfgenerator)
        if RUN_PARALLEL:
            try:
                import multiprocessing
                from multiprocessing import Pool

                import psutil
            except ImportError:
                print(
                    "\nYou don't appear to have the necessary packages "
                    "for parallelization"
                )
            syst_cores = multiprocessing.cpu_count()
            cpu_percent = psutil.cpu_percent()
            avail_cores = np.floor((100 - cpu_percent) / (100.0 / syst_cores))
            ncpu = int(np.max([1, avail_cores]))
            pool = Pool(processes=ncpu)
            pdfgenerator.parallel(ncpu=ncpu, mapfunc=pool.map)
        pdfgenerator.qdamp.value = QDAMP_I
        pdfgenerator.qbroad.value = QBROAD_I
        pdfgenerator.setQmax(QMAX)
        pdfgenerator.setQmin(QMIN)
        generators.append(pdfgenerator)
        spacegroups.append(sg)
        phase_names.append(phase_name)
    contribution.setProfile(profile, xname="r")
    ##########################################################################
    # set contribution equation

    # single nanoparticle phase refinement
    # contribution.registerFunction(
    #     sphericalCF, name="f1", argnames=["r", "psize_1"]
    # )
    # contribution.setEquation(f"s1*{phase_names[0]}*f1")

    # two phases refinement
    # contribution.setEquation(
    #     f"s1*(s2*{phase_names[0]}+(1-s2)*{phase_names[1]}))"
    # )

    # single phase refinement
    contribution.setEquation(f"s1*{phase_names[0]}")
    ##########################################################################
    recipe = FitRecipe()
    recipe.addContribution(contribution)
    for pdfgenerator, sg in zip(generators, spacegroups):
        spacegroupparams = constrainAsSpaceGroup(pdfgenerator.phase, sg)
        for par in spacegroupparams.latpars:
            recipe.addVar(
                par, fixed=False, tag="lat"
            )  # set initial value is also possible
        for par in spacegroupparams.adppars:
            recipe.addVar(par, fixed=False, tag="adp")
        for par in spacegroupparams.xyzpars:
            recipe.addVar(par, fixed=False, tag="xyz")
        recipe.addVar(
            pdfgenerator.delta2,
            fixed=False,
            value=DELTA2_I,
            tag="d2",
        )
        recipe.addVar(
            pdfgenerator.qdamp,
            fixed=False,
            name="Calib_Qdamp",
            value=QDAMP_I,
            tag="inst",
        )
        recipe.addVar(
            pdfgenerator.qbroad,
            fixed=False,
            name="Calib_Qbroad",
            value=QBROAD_I,
            tag="inst",
        )
    ###########################################################################
    # add equation parameters

    recipe.addVar(contribution.s1, value=1, tag="scale")
    # add size parameter for nanoparticle refinement
    # recipe.addVar(contribution.psize, PSIZE_I, tag="psize")

    # for multiple phase refinement, add scale restrain
    # recipe.addVar(contribution.s2, value=0.5, tag="s2")
    # recipe.constrain(contribution.s2, lb=0, ub=1)
    ###########################################################################
    for var_name, var_pack in (
        kwargs.get("previous_result", {}).get("variables", {}).items()
    ):
        if var_name in recipe._parameters:
            recipe._parameters[var_name].setValue(var_pack["value"])
    recipe.fix("all")
    tags = ["lat", "scale", "adp", "xyz", "d2", "all"]
    if "lat" not in list(recipe._tagmanager.alltags()):
        tags.remove("lat")
    if "adp" not in list(recipe._tagmanager.alltags()):
        tags.remove("adp")
    if "xyz" not in list(recipe._tagmanager.alltags()):
        tags.remove("xyz")
    for tag in tags:
        recipe.free(tag)
        least_squares(recipe.residual, recipe.values, x_scale="jac")
    fit_results = FitResults(recipe)
    results_dict = {"variables": {}}
    for name, val, unc in zip(
        fit_results.varnames, fit_results.varvals, fit_results.varunc
    ):
        results_dict["variables"][name] = {
            "value": val,
            "uncertainty": unc,
        }
    results_dict["pdf"] = {}
    results_dict["pdf"]["r"] = list(recipe.pdfcontribution.profile.x)
    results_dict["pdf"]["calculated"] = list(
        recipe.pdfcontribution.profile.ycalc
    )
    results_dict["pdf"]["observed"] = list(recipe.pdfcontribution.profile.y)
    results_dict["metrics"] = {
        "residual": fit_results.residual,
        "chi2": fit_results.chi2,
        "rchi2": fit_results.rchi2,
        "rw": fit_results.rw,
        "cumrw": list(fit_results.cumrw),
        "cumchi2": list(fit_results.cumchi2),
    }
    with open(kwargs["result_path"], "w") as f:
        json.dump(results_dict, f, indent=4)


if __name__ == "__main__":
    main(sys.argv[1])
