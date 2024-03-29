#!/usr/bin/env python3

from argparse import ArgumentParser
import Sum_gffs, Gff_creator, Samprocessor, Stats, Transcript_Annotator
from alive_progress import alive_bar
import logging
import sys
from pathlib import Path

def main():
    parser = ArgumentParser(description="This is LoRTIA: a Long-read RNA-Seq\
                            Transcript Isofom Annotator.")
    parser.add_argument("in_file",
                        help="Input file. Both .sam and .bam files are accepted.",
                        metavar="input_file")
    parser.add_argument("out_path",
                        help="Output folder. Multiple output files are going\
                        to be created using the input file's prefix (ie. the\
                        part that precedes '.bam' or '.sam')",
                        metavar="output_path")
    parser.add_argument("reference",
                        help = "The reference fasta file. Template-switching \
                        in the case of putative introns is going to be checked\
                        according to this file. It can contain multiple contigs.",
                        metavar = "reference_fasta")
    parser.add_argument("--match_score", 
                        dest="match_score",
                        help="The alignment scores for each match when searching\
                        for adapters. Penalty scores should be supplied as \
                        negative vaules. The default is: 2",
                        type=float,
                        metavar="[float]", 
                        default=2.0,
                        required=False)
    parser.add_argument("--mismatch_score", 
                        dest="mismatch_score",
                        help="The alignment scores for each mismatch when \
                        searching for adapters. Penalty scores should be \
                        supplied as negative vaules. The default is: -3",
                        metavar="[float]", 
                        default=-3.0,
                        required=False)
    parser.add_argument("--gap_open_score", 
                        dest="gap_open_score",
                        help="The alignment scores for each gap opening when\
                        searching for adapters. Penalty scores should be \
                        supplied as negative vaules. The default is: -3",
                        type=float,
                        metavar="[float]", 
                        default=-3.0,
                        required=False)
    parser.add_argument("--gap_extend_score", 
                        dest="gap_extend_score",
                        help="The alignment scores for each gap extension \
                        when searching for adapters. Penalty scores should be \
                        supplied as negative vaules. The default is: -3",
                        type=float,
                        metavar="[float]", 
                        default=-3.0,
                        required=False)
    parser.add_argument("-3", "--three_adapter", 
                        dest="three_adapter",
                        help="The 3' adapter to look for, the default is a \
                        polyA tail of 30 adenines",
                        metavar="[string]",
                        default=30*"A",
                        required=False)
    parser.add_argument("-5", "--five_adapter", 
                        dest="five_adapter",
                        help="The 5' adapter to look for. The default is the\
                        TeloPrime cap adapter: TGGATTGATATGTAATACGACTCACTATAG",
                        metavar="[string]",
                        default="TGGATTGATATGTAATACGACTCACTATAG",
                        required=False)
    parser.add_argument("--five_score", 
                        dest="five_score",
                        help="The minimum score that the adapter alignment \
                        should reach to be recognized as a 5' adapter. The \
                        default score is 20.0",
                        type=float,
                        metavar="[float]",
                        default=20.0,
                        required=False)
    parser.add_argument("--three_score", 
                        dest="three_score",
                        help="The minimum score that the adapter alignment \
                        should reach to be recognized as a 3' adapter. The \
                        default score is 20.0",
                        type=float,
                        metavar="[float]",
                        default=20.0,
                        required=False)
    parser.add_argument("--check_in_soft", 
                        dest="check_in_soft",
                        help="The number of nucleotides from the start of \
                        the soft clip where the adapter sequence is searched \
                        for. It is not advisable to search for adapters too \
                        deep into the soft clip not only because it may \
                        increase running time, but also because it increases \
                        false positive hits. The default is 30.",
                        type=int,
                        metavar="[integer]",
                        default=30,
                        required=False)
    parser.add_argument("--check_in_match", 
                        dest="check_in_match",
                        help="The number of nucleotides from the start of \
                        the soft clip where the adapter sequence is searched \
                        for. This lets adapters be discovered even if they \
                        resemble some genomic segments and therefore align to \
                        the genome. The default is 10.",
                        type=int,
                        metavar="[integer]",
                        default=10,
                        required=False)
    parser.add_argument("--check_from_alignment", 
                        dest="check_from_alignment",
                        help="The maximum distance of the adapter from the \
                        alignment. Some bases may be inserted or miscalled \
                        between the adapter and the mapping part of the read, \
                        This parameter allows those adapters to be considered \
                        'correct' which do not start exactly at the end of \
                        the mapped part but are a few bases off. The default \
                        value is 3.",
                        type=int,
                        metavar="[integer]",
                        default=3,
                        required=False)
    parser.add_argument("--shs_for_ts", 
                        dest="shs_for_ts",
                        help="The minimum length of agreement (Short \
                        Homologous sequence, SHS) between the start of the \
                        match part of the alignment and the adapter that \
                        raises a suspicion of template switching. Putative\
                        template switching artefacts are listed in a \
                        separate file and are excluded form further \
                        statistics. The value has to be lesser than the value\
                        set by --check_in_match. If greater or equal value is\
                        set, the program will not look for signs of template \
                        switching. The default value is 3 nucleotides.",
                        type=int,
                        metavar="[integer]",
                        default=3,
                        required=False)
    parser.add_argument("--first_exon", 
                        dest="first_exon",
                        help="Alignment ends are often placed far away from \
                        from the rest of the read if the adapter maps to a \
                        nearby part of the genome. This option sets the length\
                        of the first exon, under which the matching part of\
                        of the alignment should be checked for the presence of\
                        the adapters. The default is 30.",
                        type=int,
                        metavar="[integer]",
                        default=30)
    parser.add_argument("--match_in_first", 
                        dest="match_in_first",
                        help="Alignment ends are often placed far away from \
                        from the rest of the read if the adapter maps to a \
                        nearby part of the genome. With this option, the user\
                        can set how many nucleotides from the matching part \
                        of the alignment should be aligned to the adapter \
                        if at least half of the nucleotides match to the \
                        adapter, the exon will be considered false. The \
                        default is 15.",
                        type=int,
                        metavar="[integer]",
                        default=15)
    parser.add_argument("--insert_before_intron", 
                        dest="insert_before_intron",
                        help="The maximum allowed insert length immediately \
                        before an intron. Triple-chimeric reads are often \
                        as an exon, a long insert and another exon. In these \
                        cases the inserts are usually several hundred nts \
                        long and are unmapped because they stem from another \
                        contig or would be mapped to the complementary strand.\
                        The default value is 20 nts.",
                        type=int,
                        metavar="[integer]",
                        default=20,
                        required=False)
    parser.add_argument("-w", "--window",
                        dest="window",
                        help="The window that is examined when calculating \
                        the Poisson distribution. Setting low values finds \
                        false positives in a noisy data, while setting high \
                        values leads to false negatives due to the different \
                        transcriptional activity of different genomic regions.\
                        The default value is 50, which translates to a 101 nt\
                        bin (examined nucleotide +/- 50 nucleotides).",
                        type=int,
                        default=50,
                        metavar="[integer]")
    parser.add_argument("-m", "--minimum",
                        dest="minimum", 
                        help="The minimal number of reads for the feature to\
                        be accepted.",
                        type=int,
                        default=2,
                        metavar="[integer]")
    parser.add_argument("-b", "--wobble",
                        dest="wobble",
                        help="The window, in which only one of each feature \
                        is expected, and locations with lesser support are \
                        considered to be derivatives of the major. The default\
                        value is 10, which means that only one feature of a \
                        kind can be described in a 21 nt bin (location +/-10 \
                        nt). This only applies to TSSs and TESs.",
                        type=float,
                        default=10,
                        metavar="[integer]")
    parser.add_argument("-i", "--intron_wobble",
                        dest="intron_wobble",
                        help="This option is only important for error-prone \
                        reads. Sequencing errors can disrupt the mapping of \
                        introns. Rare splice juntions can be detected in the \
                        close vicinity of more frequently utilized splice\
                        junctions. The rare splice junctions are likely to \
                        be results of sequencing errors of the more frequent \
                        version. This option regulates the window in which a \
                        rare intron will be considered to have stemmed from a \
                        sequencing error. The default value is 15 nt. That \
                        means that the rare introns which are no further than \
                        15 nt away from more frequent introns, will be \
                        considered to be sequencing errors.",
                        type=int,
                        default=15,
                        metavar="[integer]")
    parser.add_argument("--rare_intron",
                        dest="rare_intron",
                        help="This option is only important for error-prone \
                        reads. Sequencing errors can disrupt the mapping of \
                        introns. Rare splice juntions can be detected in the \
                        close vicinity of more frequently utilized splice\
                        junctions. The rare splice junctions are likely to \
                        be results of sequencing errors of the more frequent \
                        version. This option determines how much rarer an \
                        should be than the most frequent intron in its +/- \
                        'intron_wobble' vicinity, in orderd to be discarded as\
                        a sequencing error. The default value is 0.05.",
                        type=float,
                        default=0.05,
                        metavar="[float]")
    parser.add_argument("-t", "--ratio",
                        dest = "ratio",
                        help = "The minimal ratio of the coverage that a feature \
                        has to reach to be accepted. The default value is 0.001.",
                        type=float,
                        default=0.001,
                        metavar="[float]")
    parser.add_argument("-d", "--distance",
                        dest="distance",
                        help="The distance from the feature position where \
                        coverage should be calculated. The default value is 15. \
                        A positive value should be given, the inward direction is \
                        calculated by the program automatically.",
                        type=int,
                        default = 15,
                        metavar="[integer]")
    parser.add_argument("--cov_sample",
                        dest="cov_sample",
                        help="The number of nucleotides where the coverage \
                        should be averaged. This many consecutive nucleotides\
                        will be considered from the 'distance' towards the \
                        feature. Its absolute value has to be smaller than \
                        or equal to the value of 'distance'. The default value\
                        is 5.",
                        type=int,
                        default=5,
                        metavar="[integer]")
    parser.add_argument("-f", "--force_consensus",
                        dest="force_consensus",
                        help="Accept only those introns which have the GTAG,\
                        GCAG, ATAC consensus sequences. Type True to enable \
                        this. By default every qualified intron is selected. ",
                        type=bool,
                        default=False,
                        metavar="[bool]")
    parser.add_argument("-s", "--significance",
                        dest="significance",
                        help="The method which should be used to filter the TSS\
                        and TES features. A single features significance can be\
                        evaluated compared to the Poisson [poisson] or the \
                        Pólya-Aeppli [polya-aeppli] distributions. The default is\
                        that every qualified feature is selected.",
                        default=False,
                        metavar="[string]")
    parser.add_argument("-g", "--gap",
                        dest="gap",
                        help="The largest allowed gap in the alignment with \
                        which it still constitutes as a transcript. Gaps are \
                        deletions which are not found in the gff of accepted \
                        introns. Such gaps can be present in chimeric reads \
                        which are often artefactual. The default value is \
                        1000.",
                        type=int,
                        default=1000,
                        metavar="[integer]")
    parser.add_argument("--mintr_count",
                        dest="mintr_count",
                        help="The minimum number of reads that has to \
                        support a transcript isoform for the isoform to be \
                        reported. The default is 1.",
                        type=int,
                        default=1,
                        metavar="[integer]")

    args = parser.parse_args()

    with alive_bar(title = "Running Modified LoRTIA") as bar:
        Samprocessor.Samprocessor(args)
        bar()

        args.coverage_file = args.prefix + "_out_minuscov.tsv"
        args.feature = "l3"
        args.feature_file = args.prefix + "_{}.tsv".format(args.feature)
        Stats.Stats(args)
        bar()

        args.coverage_file = args.prefix + "_out_pluscov.tsv"
        args.feature = "r3"
        args.feature_file = args.prefix + "_{}.tsv".format(args.feature)
        Stats.Stats(args)
        bar()

        args.coverage_file = args.prefix + "_out_minuscov.tsv"
        args.feature = "r5"
        args.feature_file = args.prefix + "_{}.tsv".format(args.feature)
        Stats.Stats(args)
        bar()

        args.coverage_file = args.prefix + "_out_pluscov.tsv"
        args.feature = "l5"
        args.feature_file = args.prefix + "_{}.tsv".format(args.feature)
        Stats.Stats(args)
        bar()

        args.coverage_file = args.prefix + "_out_allcov.tsv"
        args.feature = "in"
        args.feature_file = args.prefix + "_{}.tsv".format(args.feature)
        Stats.Stats(args)
        bar()

        # args.feature = "tss"
        # args.output_gff = False
        # Gff_creator.Gff_creator(args)
        # bar()

        # args.feature = "tes"
        # args.significance = False
        # args.output_gff = False
        # Gff_creator.Gff_creator(args)
        # bar()

        # args.feature = "intron"
        # args.output_gff = False
        # Gff_creator.Gff_creator(args)
        # bar()

        # args.in_bam = args.prefix + "_stranded_only.bam"
        # args.gff_prefix = args.prefix
        # args.output_prefix = args.prefix + "_tr"
        # Transcript_Annotator.annotate_tr(args)
        # bar()

if __name__== "__main__":
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{Path(__file__).parent}/log/LoRTIA.log"),
        logging.StreamHandler(sys.stdout)
        ]
    )
    main()