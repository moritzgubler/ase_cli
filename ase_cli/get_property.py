import argparse
from ase.io import read
import numpy as np

special_keys = [
                "energy",
                "forces",
                "stress",
                "natoms"
                ]

def parse(subparser):
    parser = subparser.add_parser("get_property", help='Prints the value of a property for a given atom in a file.')
    parser.add_argument('filename', type=argparse.FileType('r'), help='The file to average.')
    parser.add_argument('property', type=str, help='The property to get.')
    parser.add_argument('--index', type=str, help='The index of the structure to get the property for.', required = False, default = ':')
    # Set the function to be called when this command is used
    parser.set_defaults(func=main)

def main(args):
    atoms = read(args.filename.name, index=args.index)
    # print(atoms.info)
    for ats in atoms:
        if args.property not in special_keys:
            print(ats.info[args.property])
        else:
            if args.property == 'energy':
                print(ats.get_potential_energy())
            elif args.property == 'forces':
                print(ats.get_forces())
            elif args.property == "stress":
                print(ats.get_stress(voigt=False))
            elif args.property == "natoms":
                print(len(atoms))
            else:
                print("this should not happen")