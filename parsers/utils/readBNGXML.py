# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 14:28:16 2012

@author: proto
"""
from lxml import etree
import smallStructures as st
 #http://igraph.sourceforge.net/documentation.html
#----------------------------------------------------------------------


def findBond(bondDefinitions, component):
    '''
    Returns an appropiate bond number when veryfying how 
    to molecules connect in a species
    '''
    if isinstance(bondDefinitions, dict):
        return bondDefinitions.get(component)
    for idx, bond in enumerate(bondDefinitions.getchildren()):
        if component in [bond.get('site1'), bond.get('site2')]: 
            return str(idx)


    
def createMolecule(molecule, bonds):
    nameDict = {}
    mol = st.Molecule(molecule.get('name'),molecule.get('id'))
    if molecule.get('compartment') not in ['',None]:
        mol.setCompartment(molecule.get('compartment'))
    nameDict[molecule.get('id')] = molecule.get('name')
    listOfComponents = molecule.find('{http://www.sbml.org/sbml/level3}ListOfComponents')
    if listOfComponents is None:
        listOfComponents = molecule.find('.//{http://www.sbml.org/sbml/level3}ListOfComponents')
    if listOfComponents != None:
        findBond_func = findBond
        component_append = mol.addComponent
        for element in listOfComponents:
            elem_id = element.get('id')
            elem_name = element.get('name')
            elem_bonds = element.get('numberOfBonds')
            elem_state = element.get('state')

            component = st.Component(elem_name, elem_id)
            nameDict[elem_id] = elem_name
            if elem_bonds in ['+','?']:
                component.addBond(elem_bonds)
            elif elem_bonds != '0':
                component.addBond(findBond_func(bonds, elem_id))
            state = elem_state if elem_state != None else ''
            component.states.append(state)
            component.activeState = state
            component_append(component)
    return mol, nameDict
    

    
def createSpecies(pattern):
    tmpDict = {}
    species = st.Species()
    species.idx = pattern.get('id')
    mol = pattern.find('{http://www.sbml.org/sbml/level3}ListOfMolecules')
    if mol is None:
        mol = pattern.find('.//{http://www.sbml.org/sbml/level3}ListOfMolecules')
    bonds = pattern.find('{http://www.sbml.org/sbml/level3}ListOfBonds')
    if bonds is None:
        bonds = pattern.find('.//{http://www.sbml.org/sbml/level3}ListOfBonds')

    bond_map = {}
    if bonds is not None:
        for idx, bond in enumerate(bonds.getchildren()):
            bond_map[bond.get('site1')] = str(idx)
            bond_map[bond.get('site2')] = str(idx)
    else:
        bond_map = None

    for molecule in mol.getchildren():
        molecule, nameDict = createMolecule(molecule, bond_map)
        tmpDict.update(nameDict)
        species.addMolecule(molecule)
        if bonds != None:
            species.bonds = [(bond.get('site1'),bond.get('site2')) for bond in bonds]
        tmpDict.update(nameDict)
    return species, tmpDict
    
    

def parseRule(rule,parameterDict):
    '''
    Parses a rule XML section
    Returns: a list of the reactants and products used, followed by the mapping
    between the two and the list of operations that were performed
    '''
    rp = rule.find('{http://www.sbml.org/sbml/level3}ListOfReactantPatterns')
    if rp is None:
        rp = rule.find('.//{http://www.sbml.org/sbml/level3}ListOfReactantPatterns')
    pp = rule.find('{http://www.sbml.org/sbml/level3}ListOfProductPatterns')
    if pp is None:
        pp = rule.find('.//{http://www.sbml.org/sbml/level3}ListOfProductPatterns')
    mp = rule.find('{http://www.sbml.org/sbml/level3}Map')
    if mp is None:
        mp = rule.find('.//{http://www.sbml.org/sbml/level3}Map')
    op = rule.find('{http://www.sbml.org/sbml/level3}ListOfOperations')
    if op is None:
        op = rule.find('.//{http://www.sbml.org/sbml/level3}ListOfOperations')
    rt = rule.find('{http://www.sbml.org/sbml/level3}RateLaw')
    if rt is None:
        rt = rule.find('.//{http://www.sbml.org/sbml/level3}RateLaw')
    nameDict = {}
    reactants = []
    products = []
    actions = []
    mappings = []
    
    if len(rp) == 0:
        sp = st.Species()
        ml = st.Molecule('0','')
        sp.addMolecule(ml)
        reactants.append(sp)
    if len(pp) == 0:
        sp = st.Species()
        ml = st.Molecule('0','')
        sp.addMolecule(ml)
        products.append(sp)
    if rp is not None:
        for pattern in rp:
            elm, tmpDict = createSpecies(pattern)
            reactants.append(elm)
            nameDict.update(tmpDict)
    if pp is not None:
        for pattern in pp:
            elm, tmpDict = createSpecies(pattern)
            products.append(elm)
            nameDict.update(tmpDict)
    if op is not None:
        for operation in op:
            action = st.Action()
            tag = operation.tag
            tag = tag.replace('{http://www.sbml.org/sbml/level3}','')
            if operation.get('site1') != None:
                action.setAction(tag, operation.get('site1'), operation.get('site2'))
            else:
                action.setAction(tag, operation.get('site'), None)
            actions.append(action)
    if mp is not None:
        for mapping in mp:
            tmpMap = (mapping.get('sourceID'), mapping.get('targetID'))
            mappings.append(tmpMap)

    if rt is not None:
        rateConstants = rt.find('{http://www.sbml.org/sbml/level3}ListOfRateConstants')
        if rateConstants is None:
            rateConstants = rt.find('.//{http://www.sbml.org/sbml/level3}ListOfRateConstants')
        if rateConstants == None:
            rateConstants = rt.get('name')
        else:
            for constant in rateConstants:
                tmp = constant.get('value')
            rateConstants = tmp
    else:
        rateConstants = None
    rateConstantsValue = parameterDict[rateConstants] if rateConstants in parameterDict else rateConstants
    #rule = st.Rule()   
    label = rule.get('name')
    label = label.replace('(','_').replace(')','_')
    rule = st.Rule(label)
    rule.addReactantList(reactants)
    rule.addProductList(products)
    rule.addActionList(actions)
    rule.addMappingList(mappings)
    rule.addRate(rateConstants)
    
    #return reactants, products, actions, mappings, nameDict,rateConstantsValue,rateConstants
    return rule,nameDict,rateConstantsValue,rateConstants
    
def parseMolecules(molecules):
    '''
    Parses an XML molecule section
    Returns: a molecule structure
    '''

    mol = st.Molecule(molecules.get('id'),molecules.get('id'))
    components = molecules.find('{http://www.sbml.org/sbml/level3}ListOfComponentTypes')
    if components is None:
        components = molecules.find('.//{http://www.sbml.org/sbml/level3}ListOfComponentTypes')
    if components != None:
        for component in components:
            comp = parseComponent(component)
            mol.addComponent(comp)
    return mol       
        
def parseComponent(component):
    '''
    parses  a bngxml molecule types section
    '''
    comp = st.Component(component.get('id'),component.get('id'))
    states = component.find('{http://www.sbml.org/sbml/level3}ListOfAllowedStates')
    if states is None:
        states = component.find('.//{http://www.sbml.org/sbml/level3}ListOfAllowedStates')
    if states != None:
        for state in states:
            comp.addState(state.get('id'))
    return comp
    
def parseXML(xmlFile):
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    doc = etree.parse(xmlFile, parser)
    molecules = doc.findall('.//{http://www.sbml.org/sbml/level3}MoleculeType')
    rules = doc.findall('.//{http://www.sbml.org/sbml/level3}ReactionRule')
    ruleDescription = []
    moleculeList = []

    parameters = doc.findall('.//{http://www.sbml.org/sbml/level3}Parameter')
    parameterDict = {}
    for parameter in parameters:
        parameterDict[parameter.get('id')] = parameter.get('value')

    for molecule in molecules:
        moleculeList.append(parseMolecules(molecule))
        
    for rule in rules:
        description = parseRule(rule,parameterDict)
        #if 'reverse' in description[0].label:
        #    ruleDescription[-1][0].bidirectional= True
        #    ruleDescription[-1][0].rates.append(description[0].rates[0])
        #else:
        ruleDescription.append(parseRule(rule,parameterDict))
    return moleculeList, ruleDescription,parameterDict
        
def getNumObservablesXML(xmlFile):
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    doc = etree.parse(xmlFile, parser)
    observables = doc.findall('.//{http://www.sbml.org/sbml/level3}Observable')
    return len(observables)
    
if __name__ == "__main__":
    #mol,rule,par = parseXML("output19.xml")
    #print [str(x) for x in mol]
    print(getNumObservablesXML('output19.xml'))