import argparse
import ase_cli.average_file
import ase_cli.convert_ase_files
import ase_cli.get_property
import ase_cli.qe_input
import ase_cli.rattle
import ase_cli.rotate
import ase_cli.supercell

def main():
    """
    Main function for the ASE Command Line Interface
    This function parses the command line arguments and calls the appropriate function.

    How to add a new command:
    1. Create a new file in the ase_cli directory.
    2. Create a function in the new file that takes a subparser as an argument and adds the necessary arguments.
    3. Dont forget to call set_defaults(func=my_function) of the parser object with the function that implements the command (argparse will automatically call this function).
    4. Implement the functionality of the command in the new file in a function. The function should take the parsed arguments as an argument.
    5. Import the new file in this file.
    6. Call the parse function of the new file in the main function.
    """

    parser = argparse.ArgumentParser(description='ASE Command Line Interface')
    subparser = parser.add_subparsers(help="Command that database will execute", dest='command', required=True)

    # Add the parsers for the commands here
    ase_cli.average_file.parse(subparser)
    ase_cli.convert_ase_files.parse(subparser)
    ase_cli.supercell.parse(subparser)
    ase_cli.rattle.parse(subparser)
    ase_cli.get_property.parse(subparser)
    ase_cli.qe_input.parse(subparser)
    ase_cli.rotate.parse(subparser)

    # Parse the arguments
    main_args = parser.parse_args()
    # Argparse will call the function that is set as default for the command.
    main_args.func(main_args)

if __name__ == '__main__':
    main()