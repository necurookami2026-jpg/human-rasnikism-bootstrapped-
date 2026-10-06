#!/usr/bin/env python3
"""Exact rational arithmetic for a declared seven-sample rainbow exercise."""
from fractions import Fraction
import argparse
import json
from pathlib import Path

C = 299792458  # SI speed of light in vacuum, metres per second
SAMPLES = (('red', 700), ('orange', 620), ('yellow', 580), ('green', 530),
           ('blue', 470), ('indigo', 445), ('violet', 400))


def frequency(wavelength_nm):
    """Return exact Hz for a positive rational vacuum wavelength in nm."""
    wavelength = Fraction(wavelength_nm)
    if wavelength <= 0:
        raise ValueError('Wavelength must be positive')
    return Fraction(C * 10**9, 1) / wavelength


def record():
    return {'format': 'sciencerainbowrainbowscience-computerwork', 'version': 1,
            'speed_of_light_m_per_s': C,
            'scope': 'Exact arithmetic on declared samples; not measured colour boundaries or a complete optical simulation.',
            'samples': [{'colour': colour, 'wavelength_nm': str(nm),
                         'frequency_hz': str(frequency(nm)),
                         'roundtrip_nm': str(Fraction(C * 10**9, 1) / frequency(nm))}
                        for colour, nm in SAMPLES]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write a new JSON exercise record; refuses overwriting')
    args = parser.parse_args()
    payload = json.dumps(record(), indent=2) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(payload)
    else:
        print(payload, end='')


if __name__ == '__main__':
    main()
