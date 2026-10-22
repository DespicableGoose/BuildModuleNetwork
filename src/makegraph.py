# -*- coding: utf-8 -*-

# This script is responsible for building the graph using BFS.

from typing import Literal

import requestpage, pickle, json, os

PageType = Literal['module'] | Literal['data'] | Literal['external'] | Literal['test']

def buildGraph():
    # Define a list of starting pages for BFS. In this case, we request all module pages from API
    # and filter it using custom rules
    # 
    # This list can also be self-defined!
    # For example, using just ["Pet"], the BFS will give 88 modules!
    # If there are any pages that are not "dependency-linked" with existing starting pages,
    # append those items to the following list so that they can be BFS-ed
    startFromPages = requestpage.requestListOfAllPages(828, "Module:")

    print(f"Number of starting pages: {len(startFromPages)}")

    # Fetch each page content: detect require(), mw.loadData(), loader.require(), and loader.loadData()
    # Using BFS, build dependencies graph
    queue: list[str] = []
    dependenciesGraph: dict[str, list[str]] = {}
    pageTypes: dict[str, PageType] = {}

    for pg in startFromPages:
        name = pg.replace("Module:", "")
        queue.append(name)

    while len(queue) > 0:
        name = queue.pop(0).strip()
        name = requestpage.standardizeName(name)
        if name != "" and not name in dependenciesGraph:
            print("Finding dependencies for", name)
            dependencies, dataDependencies, isExternal = requestpage.findDependencies(name)
            combinedDependencies = dependencies + dataDependencies
            dependenciesGraph[name] = combinedDependencies
            queue += combinedDependencies
            print("External" if isExternal else combinedDependencies)

            for dataPage in dataDependencies:
                # detected to be a data page
                pageTypes[dataPage] = "data"

            dataKeywords = ["Data", "Aliases", "Datasheet", "i18n"]
            if isExternal:
                pageTypes[name] = "external"
            elif name.endswith("testcases"):
                pageTypes[name] = "test"
            elif any(name.endswith(word) for word in dataKeywords):
                pageTypes[name] = "data"
            elif name not in pageTypes:
                # assign default if not been assigned a type
                pageTypes[name] = "module"

    print(dependenciesGraph)
    print(len(dependenciesGraph))

    return dependenciesGraph, pageTypes

def saveGraph(dependenciesGraph: dict[str, list[str]], pageTypes: dict[str, PageType]):
    os.makedirs("build", exist_ok=True)

    with open("build/dependencies-graph.txt", "w") as f:
        f.write(json.dumps(dependenciesGraph, indent=4))
        f.close()

    with open('build/dependencies-graph.pickle', 'wb') as f:
        pickle.dump(dependenciesGraph, f)

    with open("build/pagetypes.txt", "w") as f:
        f.write(json.dumps(pageTypes, indent=4))
        f.close()

    with open('build/pagetypes.pickle', 'wb') as f:
        pickle.dump(pageTypes, f)

if __name__ == "__main__":
    dependenciesGraph, pageTypes = buildGraph()
    saveGraph(dependenciesGraph, pageTypes)
