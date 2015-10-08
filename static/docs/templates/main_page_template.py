__author__ = 'pavel'

MAIN_PAGE_MD = """
# miXGENE
miXGENE is a web-based tool for machine learning from heterogeneous omics data using prior knowledge. It is primarily designed to facilitate the integrated analysis of mRNA, miRNA and DNA methylation data. It fuses the data using the existing knowledge on their interaction (KEGG pathways, miRNA targets, protein-protein interaction networks, MSigDB terms, GO terms) and delivers both predictive and descriptive models that explain the measurements and comply with the provided knowledge. In terms of descriptive analysis, miXGENE allows to identify the individual measured entities and their whole comodules differentially expressed in the data under study including the follow-up  enrichment analysis. In terms of predictive modelling, miXGENE constructs classifiers that distinguish between the individual phenotypes. The main criteria in classifier construction are classification accuracy and interpretability in terms of the existing knowledge.
miXGENE is a workflow management system. The user defines his task/experiment as a workflow, the system provides a workspace to freely define the workflow from the available functional blocks. The user can interactively create, modify and execute his/her workflow. The user first creates and names the workflow. Then, the individual blocks are gradually added from the block pallette. The blocks get connected through setting their inputs and outputs. A particular execution of a workflow with the given settings is referred to as run, each run is stored in the system and can later be accessed by the user. During the automated workflow execution, all time consuming tasks are dispatched through an asynchronous task queue. The user learns about the outcome of his experiment from the output blocks that report the reached results. The results can be exported from the system into csv or JSON files, miXGENE contains a set of built-in visualisation tools too. The execution can be continuously followed in the workflow log. The log helps namely when tracking a time consuming experiment or an invalid workflow.

## Workflow management system keywords
* [workflow](workflow/index.html) - implements an experiment as a sequence of interconnected and appropriately parametrized miXGENE blocks
* experiment - a logical sequence of steps that serves to confirm of reject a hypothesis, takes a set of input data and delivers a result, in miXGENE it get implemented as a workflow
* functional block - implements a particular functionality, the description of the individual blocks is provided in technical documentation
* meta-block - creates a sub-scope, where sub-workflow can be defined, the primary usage of meta-blocks is in repeated execution of the workflow part that lies in the sub-scope
* run - a particular execution of a workflow with the given inputs, settings and the particular outcome
* workspace - the main interface between the user and miXGENE when constructing a workflow, the user defines a workflow and executes it here, each workflow has its own workspace, in the beginning it is empty
* scope - the scope includes all the blocks and their inputs and outupts available in terms of the given workflow, the root scope correspond to the whole workflow, the sub-scopes originate inside the individual meta-blocks to restrain the availability of their internal blocks

The data structures available to the user are presented [here](data_types.html).
The description of the individual blocks is provided in technical documentation. The workflow examples are provided ..., there are also a few tutorials that demonstrate workflow construction on the fly.

## References
Holec, M., Gologuzov, V., Klema, J.: miXGENE Tool for Learning from Heterogeneous Gene Expression Data Using Prior Knowledge. In Proceedings of 27th International Symposium on Computer-Based Medical Systems, Los Alamitos: IEEE Computer Society, pp. 247-250, 2014. (http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=6881885),  (http://ida.felk.cvut.cz/klema/publications/Biotex/cbms2014.pdf)

"""


MAIN_PAGE_HTML = """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
  <meta name="viewport" content="width=device-width">

  <title>miXGENE</title>

  <!-- Flatdoc -->
  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
  <script src='https://cdn.rawgit.com/rstacruz/flatdoc/v0.9.0/legacy.js'></script>
  <script src='https://cdn.rawgit.com/rstacruz/flatdoc/v0.9.0/flatdoc.js'></script>

  <!-- Flatdoc theme -->
  <link  href='https://cdn.rawgit.com/rstacruz/flatdoc/v0.9.0/theme-white/style.css' rel='stylesheet'>
  <script src='https://cdn.rawgit.com/rstacruz/flatdoc/v0.9.0/theme-white/script.js'></script>

  <!-- Meta -->
  <meta content="miXGENE" property="og:title">
  <meta content="Platform for analysis of gene expression data." name="description">

  <!-- Initializer -->
  <script>
    Flatdoc.run({
        fetcher: Flatdoc.file('index.md')
    });
  </script>
</head>
<body role='flatdoc' class='no-literate'>

  <div class='header'>
    <div class='left'>
      <h1>miXGENE</h1>
      <ul>
        <li><a href='https://github.com/strny/miXGENE'>View on GitHub</a></li>
        <li><a href='https://github.com/strny/miXGENE/issues'>Issues</a></li>
      </ul>
    </div>
    <div class='right'>
      <!-- GitHub buttons: see http://ghbtns.com -->
      <iframe src="http://ghbtns.com/github-btn.html?strny=strny&amp;miXGENE=miXGENE&amp;type=watch&amp;count=true" allowtransparency="true" frameborder="0" scrolling="0" width="110" height="20"></iframe>
    </div>
  </div>

  <div class='content-root'>
    <div class='menubar'>
      <div class='menu section' role='flatdoc-menu'>
      </div>
    </div>
    <div role='flatdoc-content' class='content'></div>
  </div>

</body>
</html>
"""
