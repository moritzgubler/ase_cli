from ase.io import read, write
import argparse
import numpy as np
import os

def parse(subparser):
    parser = subparser.add_parser("rotate", help="Rotate structure so z-axis points to specified direction.")
    parser.add_argument('filename', type=argparse.FileType('r'), help='The file to rotate.')
    parser.add_argument('direction', type=float, nargs=3, help='Target direction vector (x y z).')
    parser.add_argument('--output', type=str, help='The output file. Default: input file with _rotated appended.', required=False)
    parser.add_argument('--input-format', type=str, help='Input file format (e.g., xyz, cif, vasp, etc.).', required=False)
    parser.add_argument('--output-format', type=str, help='Output file format (default: extxyz).', default='extxyz', required=False)
    parser.add_argument('--index', type=str, help='Index of structure(s) to read (default: 0, use ":" for all).', default='0', required=False)
    parser.set_defaults(func=rotate)


def rodrigues_rotation(vector, axis, angle):
    """
    Rotate a vector around an axis by an angle using Rodrigues' rotation formula.

    Parameters:
    -----------
    vector : array_like
        The vector to rotate
    axis : array_like
        The rotation axis (will be normalized)
    angle : float
        The rotation angle in radians

    Returns:
    --------
    ndarray
        The rotated vector
    """
    axis = axis / np.linalg.norm(axis)
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    # Rodrigues' rotation formula:
    # v_rot = v*cos(theta) + (k x v)*sin(theta) + k*(k.v)*(1-cos(theta))
    rotated = (vector * cos_angle +
               np.cross(axis, vector) * sin_angle +
               axis * np.dot(axis, vector) * (1 - cos_angle))

    return rotated


def rotation_matrix_rodrigues(axis, angle):
    """
    Compute rotation matrix using Rodrigues' formula.

    Parameters:
    -----------
    axis : array_like
        The rotation axis (will be normalized)
    angle : float
        The rotation angle in radians

    Returns:
    --------
    ndarray
        3x3 rotation matrix
    """
    axis = axis / np.linalg.norm(axis)
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    # Cross-product matrix for the axis
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])

    # Rodrigues' rotation matrix formula:
    # R = I + sin(theta)*K + (1-cos(theta))*K^2
    R = np.eye(3) + sin_angle * K + (1 - cos_angle) * np.dot(K, K)

    return R


def compute_rotation_to_direction(target_direction):
    """
    Compute rotation matrix to rotate z-axis to target direction.

    Parameters:
    -----------
    target_direction : array_like
        The target direction vector (will be normalized)

    Returns:
    --------
    ndarray
        3x3 rotation matrix
    """
    # Normalize the target direction
    target = np.array(target_direction, dtype=float)
    target = target / np.linalg.norm(target)

    # Initial z-axis
    z_axis = np.array([0, 0, 1])

    # Check if target is already aligned with z-axis
    dot_product = np.dot(z_axis, target)
    if np.abs(dot_product - 1.0) < 1e-10:
        # Already aligned
        return np.eye(3)
    elif np.abs(dot_product + 1.0) < 1e-10:
        # Opposite direction - rotate 180 degrees around x-axis
        return np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])

    # Rotation axis: perpendicular to both z and target
    rotation_axis = np.cross(z_axis, target)

    # Rotation angle
    angle = np.arccos(dot_product)

    # Compute rotation matrix
    return rotation_matrix_rodrigues(rotation_axis, angle)


def rotate(args):
    if args.input_format:
        atoms = read(args.filename, index=args.index, format=args.input_format)
    else:
        atoms = read(args.filename, index=args.index)
    args.filename.close()

    # Ensure atoms is always a list for consistent processing
    if not isinstance(atoms, list):
        atoms = [atoms]

    # Get target direction from arguments
    target_direction = np.array(args.direction)

    # Compute rotation matrix
    rotation_matrix = compute_rotation_to_direction(target_direction)

    # Print rotation matrix with nice formatting
    normalized_direction = target_direction / np.linalg.norm(target_direction)
    print(f"\nRotation matrix (z-axis -> [{normalized_direction[0]:.6f}, {normalized_direction[1]:.6f}, {normalized_direction[2]:.6f}]):")
    for row in rotation_matrix:
        print(f"  [{row[0]:9.6f}  {row[1]:9.6f}  {row[2]:9.6f}]")

    # Apply rotation to all structures
    for ats in atoms:
        # Rotate atomic positions
        positions = ats.get_positions()
        rotated_positions = positions @ rotation_matrix.T
        ats.set_positions(rotated_positions)

        # Rotate cell if it exists
        if ats.cell is not None and np.any(ats.cell):
            cell = ats.get_cell()
            rotated_cell = cell @ rotation_matrix.T
            ats.set_cell(rotated_cell, scale_atoms=False)

    # Determine output filename
    if args.output is None:
        base_name = os.path.splitext(args.filename.name)[0]
        output = base_name + "_rotated." + args.output_format
    else:
        output = args.output

    # Write output using output-format
    write(output, atoms, format=args.output_format)

    print(f"\nRotated structure written to {output}")
    print(f"Target direction: {target_direction / np.linalg.norm(target_direction)}")
