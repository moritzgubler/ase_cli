from ase.io import read
from ase.io.espresso import write_espresso_in
import os

def parse(subparser):
    parser = subparser.add_parser("qe_input", help='Writes a minimal Quantum ESPRESSO input file from a structure file.')
    parser.add_argument('input', type=str, help='The structure file to read.')
    parser.add_argument('--pseudodir', type=str, help='Path to the pseudopotential directory', required=True)
    parser.add_argument('--output', type=str, help='The output file name. Default: qe.in', default='qe.in')
    parser.add_argument('--index', type=str, help='The index of the structure to use. Default: -1 (last structure)', default='-1')
    parser.add_argument('--input_format', type=str, help='The input format. Default: ase will choose format based on file extension', default=None)
    parser.add_argument('--kpts', type=str, help='K-points grid as "nx ny nz" (e.g., "4 4 4"). Default: 1 1 1', default='1 1 1')
    parser.add_argument('--koffset', type=str, help='K-points offset as "sx sy sz" (e.g., "0 0 0"). Default: 0 0 0', default='0 0 0')
    parser.add_argument('--ecutwfc', type=float, help='Kinetic energy cutoff for wavefunctions in Ry. Default: 80', default=80.0)
    parser.add_argument('--ecutrho', type=float, help='Kinetic energy cutoff for charge density in Ry. Default: 800', default=800.0)
    parser.add_argument('--degauss', type=float, help='Gaussian spreading for smearing in Ry. Default: 1e-10', default=1.0e-10)
    parser.add_argument('--mixing-beta', type=float, help='Mixing factor for self-consistency. Default: 0.4', default=0.4)
    # Set the function to be called when this command is used
    parser.set_defaults(func=main)

def find_pseudopotentials(pseudodir, elements):
    """
    Find pseudopotential files for given elements in the pseudodir.
    Matches element symbols (case-insensitive) at the beginning of filenames.
    """
    pseudos = {}

    if not os.path.isdir(pseudodir):
        raise ValueError(f"Pseudopotential directory not found: {pseudodir}")

    # List all files in the directory
    pseudo_files = os.listdir(pseudodir)

    for element in elements:
        # Try to find a file that starts with the element symbol (case-insensitive)
        found = False
        for filename in pseudo_files:
            if filename.lower().startswith(element.lower()):
                pseudos[element] = filename
                found = True
                break

        if not found:
            raise ValueError(f"No pseudopotential file found for element '{element}' in {pseudodir}")

    return pseudos

def main(args):
    """
    Reads a structure file and writes a minimal Quantum ESPRESSO input file.
    """
    # Read the structure
    atoms = read(args.input, index=args.index, format=args.input_format)

    # Get unique elements in the structure
    elements = set(atoms.get_chemical_symbols())

    # Find pseudopotential files
    pseudopotentials = find_pseudopotentials(args.pseudodir, elements)

    # Parse k-points
    kpts = [int(k) for k in args.kpts.split()]
    koffset = [int(k) for k in args.koffset.split()]

    if len(kpts) != 3:
        raise ValueError("K-points must be specified as three integers (e.g., '4 4 4')")
    if len(koffset) != 3:
        raise ValueError("K-offset must be specified as three integers (e.g., '0 0 0')")

    # Minimal input parameters for Quantum ESPRESSO
    input_data = {
        'control': {
            'calculation': 'scf',
            'pseudo_dir': args.pseudodir,
        },
        'system': {
            'occupations': 'smearing',
            'smearing': 'gaussian',
            'degauss': args.degauss,
            'ecutwfc': args.ecutwfc,
            'ecutrho': args.ecutrho,
        },
        'electrons': {
            'conv_thr': 1.0e-10,
            'mixing_beta': args.mixing_beta,
        },
    }

    # Write the QE input file
    with open(args.output, 'w') as f:
        write_espresso_in(f, atoms, input_data=input_data, pseudopotentials=pseudopotentials, kpts=kpts, koffset=koffset)

    print(f"Quantum ESPRESSO input written to {args.output}")
