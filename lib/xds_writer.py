import os

if not 'FAST_DP_ROOT' in os.environ:
    raise RuntimeError, 'FAST_DP_ROOT undefined'

from run_job import get_number_cpus

# XDS.INP writer functions - two (three) of these, to write out commands
# for autoindexing, integration then postrefinement and scaling. Split
# up thus because XDS will frequently stop after autoindexing complaining
# that your data are not perfect, and then you probably want to run post-
# refinement and scaling a couple of times. With the latter need to be able
# to control the scale factors applied. N.B. these calculate the image
# ranges to use from the input metadata.

def write_xds_inp_autoindex(metadata, xds_inp):

    fout = open(xds_inp, 'w')

    template = os.path.join(os.environ['FAST_DP_ROOT'],
                            'lib', 'templates',
                            '%s_INDEX.INP' % metadata['detector'])

    if not os.path.exists(template):
        raise RuntimeError, 'template for %s not found at %s' % \
              (metadata['detector'], template)

    template_str = open(template, 'r').read().strip()

    # should somehow hang this from an anomalous flag

    friedels_law = 'FALSE'

    fout.write('%s\n' % template_str.format(
        no_processors = get_number_cpus(),
        nx = metadata['size'][0],
        ny = metadata['size'][1],
        qx = metadata['pixel'][0],
        qy = metadata['pixel'][1],
        orgx = metadata['beam'][0] / metadata['pixel'][0],
        orgy = metadata['beam'][1] / metadata['pixel'][1],
        distance = metadata['distance'],
        sensor = metadata.get('sensor', None),
        wavelength = metadata['wavelength'],
        oscillation = metadata['oscillation'][1],
        friedels_law = friedels_law,
        template = os.path.join(metadata['directory'],
                                metadata['template'].replace('#', '?')),
        starting_angle = metadata['oscillation'][0],
        starting_image = metadata['start']))

    # then we get the non-template stuff

    fout.write('DATA_RANGE=%d %d\n' % (metadata['start'],
                                       metadata['end']))

    # compute the background range as min(all, 5)

    if metadata['end'] - metadata['start'] > 5:
        fout.write('BACKGROUND_RANGE=%d %d\n' % \
                   (metadata['start'], metadata['start'] + 5))
    else:
        fout.write('BACKGROUND_RANGE=%d %d\n' % (metadata['start'],
                                                 metadata['end']))

    # by default autoindex off all images - can make this better later on.
    # Ok: I think it is too slow already. Three wedges, as per xia2...
    # that would be 5 images per wedge, then. Erk. Should be *degrees*

    images = range(metadata['start'], metadata['end'] + 1)

    wedge_size = int(round(5.0  / metadata['oscillation'][1])) - 1

    wedge = (images[0], images[0] + wedge_size)
    fout.write('SPOT_RANGE=%d %d\n' % wedge)

    # if we have more than 90 degrees of data, use wedges at the start,
    # 45 degrees in and 90 degrees in, else use a wedge at the start,
    # one in the middle and one at the end.

    # if less than 15 degrees of data, use all of the images

    if (metadata['end'] - metadata['start']) * metadata['oscillation'][1] < 15:
        fout.write('SPOT_RANGE=%d %d\n' % (metadata['start'],
                                           metadata['end']))

    elif int(90.0 / metadata['oscillation'][1]) + wedge_size in images:
        wedge = (int(45.0 / metadata['oscillation'][1]),
                 int(45.0 / metadata['oscillation'][1]) + wedge_size)
        fout.write('SPOT_RANGE=%d %d\n' % wedge)
        wedge = (int(90.0 / metadata['oscillation'][1]),
                 int(90.0 / metadata['oscillation'][1]) + wedge_size)
        fout.write('SPOT_RANGE=%d %d\n' % wedge)

    else:
        mid = (len(images) / 2) - wedge_size + images[0] - 1
        wedge = (mid, mid + wedge_size)
        fout.write('SPOT_RANGE=%d %d\n' % wedge)
        wedge = (images[-5], images[-1])
        fout.write('SPOT_RANGE=%d %d\n' % wedge)

    fout.close()

    return

def write_xds_inp_autoindex_p1_cell(metadata, xds_inp, cell):

    fout = open(xds_inp, 'w')

    template = os.path.join(os.environ['FAST_DP_ROOT'],
                            'lib', 'templates',
                            '%s_INDEX.INP' % metadata['detector'])

    if not os.path.exists(template):
        raise RuntimeError, 'template for %s not found at %s' % \
              (metadata['detector'], template)

    template_str = open(template, 'r').read().strip()

    # should somehow hang this from an anomalous flag

    friedels_law = 'FALSE'

    fout.write('%s\n' % template_str.format(
        no_processors = get_number_cpus(),
        nx = metadata['size'][0],
        ny = metadata['size'][1],
        qx = metadata['pixel'][0],
        qy = metadata['pixel'][1],
        orgx = metadata['beam'][0] / metadata['pixel'][0],
        orgy = metadata['beam'][1] / metadata['pixel'][1],
        distance = metadata['distance'],
        sensor = metadata.get('sensor', None),
        wavelength = metadata['wavelength'],
        oscillation = metadata['oscillation'][1],
        friedels_law = friedels_law,
        template = os.path.join(metadata['directory'],
                                metadata['template'].replace('#', '?')),
        starting_angle = metadata['oscillation'][0],
        starting_image = metadata['start']))

    # cell, spacegroup

    fout.write('SPACE_GROUP_NUMBER=1\n')
    fout.write('UNIT_CELL_CONSTANTS=%f %f %f %f %f %f\n' % tuple(cell))

    # then we get the non-template stuff

    fout.write('DATA_RANGE=%d %d\n' % (metadata['start'],
                                       metadata['end']))

    # compute the background range as min(all, 5)

    if metadata['end'] - metadata['start'] > 5:
        fout.write('BACKGROUND_RANGE=%d %d\n' % \
                   (metadata['start'], metadata['start'] + 5))
    else:
        fout.write('BACKGROUND_RANGE=%d %d\n' % (metadata['start'],
                                                 metadata['end']))

    # by default autoindex off all images - can make this better later on.
    # Ok: I think it is too slow already. Three wedges, as per xia2...
    # that would be 5 images per wedge, then. Erk. Should be *degrees*

    images = range(metadata['start'], metadata['end'] + 1)

    wedge_size = int(round(5.0  / metadata['oscillation'][1])) - 1

    wedge = (images[0], images[0] + wedge_size)
    fout.write('SPOT_RANGE=%d %d\n' % wedge)

    # if we have more than 90 degrees of data, use wedges at the start,
    # 45 degrees in and 90 degrees in, else use a wedge at the start,
    # one in the middle and one at the end.

    # if less than 15 degrees of data, use all of the images

    if (metadata['end'] - metadata['start']) * metadata['oscillation'][1] < 15:
        fout.write('SPOT_RANGE=%d %d\n' % (metadata['start'],
                                           metadata['end']))

    elif int(90.0 / metadata['oscillation'][1]) + wedge_size in images:
        wedge = (int(45.0 / metadata['oscillation'][1]),
                 int(45.0 / metadata['oscillation'][1]) + wedge_size)
        fout.write('SPOT_RANGE=%d %d\n' % wedge)
        wedge = (int(90.0 / metadata['oscillation'][1]),
                 int(90.0 / metadata['oscillation'][1]) + wedge_size)
        fout.write('SPOT_RANGE=%d %d\n' % wedge)

    else:
        mid = (len(images) / 2) - wedge_size + images[0] - 1
        wedge = (mid, mid + wedge_size)
        fout.write('SPOT_RANGE=%d %d\n' % wedge)
        wedge = (images[-5], images[-1])
        fout.write('SPOT_RANGE=%d %d\n' % wedge)

    fout.close()

    return

def write_xds_inp_integrate(metadata, xds_inp, resolution_low, no_jobs=1, no_processors=0):

    # FIXME in here calculate the maximum number of jobs to correspond at the
    # least to 5 degree wedges / job.

    fout = open(xds_inp, 'w')

    template = os.path.join(os.environ['FAST_DP_ROOT'],
                            'lib', 'templates',
                            '%s_INTEGRATE.INP' % metadata['detector'])

    if not os.path.exists(template):
        raise RuntimeError, 'template for %s not found at %s' % \
              (metadata['detector'], template)

    template_str = open(template, 'r').read().strip()

    # should somehow hang this from an anomalous flag

    friedels_law = 'FALSE'

    if no_processors == 0:
        no_processors = get_number_cpus()

    fout.write('%s\n' % template_str.format(
        no_processors = no_processors,
        no_jobs = no_jobs,
        resolution_low = resolution_low,
        resolution_high = 0.0,
        nx = metadata['size'][0],
        ny = metadata['size'][1],
        qx = metadata['pixel'][0],
        qy = metadata['pixel'][1],
        orgx = metadata['beam'][1] / metadata['pixel'][1],
        orgy = metadata['beam'][0] / metadata['pixel'][0],
        distance = metadata['distance'],
        sensor = metadata.get('sensor', None),
        wavelength = metadata['wavelength'],
        oscillation = metadata['oscillation'][1],
        friedels_law = friedels_law,
        template = os.path.join(metadata['directory'],
                                metadata['template'].replace('#', '?')),
        starting_angle = metadata['oscillation'][0],
        starting_image = metadata['start']))

    # then we get the non-template stuff

    fout.write('DATA_RANGE=%d %d\n' % (metadata['start'],
                                       metadata['end']))

    fout.close()

    return

# N.B. this one is a little different to the others as the inclusion of
# the cell constants and symmetry are *mandatory*. N.B. default may be
# to use the triclinic solution in the first pass.

def write_xds_inp_correct(metadata, unit_cell, space_group_number,
                          xds_inp, scale = True,
                          resolution_low = 30, resolution_high = 0.0):

    fout = open(xds_inp, 'w')

    template = os.path.join(os.environ['FAST_DP_ROOT'],
                            'lib', 'templates',
                            '%s_CORRECT.INP' % metadata['detector'])

    if not os.path.exists(template):
        raise RuntimeError, 'template for %s not found at %s' % \
              (metadata['detector'], template)

    template_str = open(template, 'r').read().strip()

    # should somehow hang this from an anomalous flag

    if 'atom' in metadata:
        friedels_law = 'FALSE'
    else:
        friedels_law = 'TRUE'

    if scale:
        corrections = 'ALL'
    else:
        corrections = '!'

    fout.write('%s\n' % template_str.format(
        no_processors = get_number_cpus(),
        resolution_low = resolution_low,
        resolution_high = resolution_high,
        unit_cell_a = unit_cell[0],
        unit_cell_b = unit_cell[1],
        unit_cell_c = unit_cell[2],
        unit_cell_alpha = unit_cell[3],
        unit_cell_beta = unit_cell[4],
        unit_cell_gamma = unit_cell[5],
        space_group_number = space_group_number,
        nx = metadata['size'][0],
        ny = metadata['size'][1],
        qx = metadata['pixel'][0],
        qy = metadata['pixel'][1],
        orgx = metadata['beam'][1] / metadata['pixel'][1],
        orgy = metadata['beam'][0] / metadata['pixel'][0],
        distance = metadata['distance'],
        sensor = metadata.get('sensor', None),
        wavelength = metadata['wavelength'],
        oscillation = metadata['oscillation'][1],
        friedels_law = friedels_law,
        corrections = corrections,
        template = os.path.join(metadata['directory'],
                                metadata['template'].replace('#', '?')),
        starting_angle = metadata['oscillation'][0],
        starting_image = metadata['start']))

    # then we get the non-template stuff

    fout.write('DATA_RANGE=%d %d\n' % (metadata['start'],
                                       metadata['end']))

    fout.close()

    return

def write_xds_inp_correct_no_cell(metadata,
                                  xds_inp, scale = True,
                                  resolution_low = 30, resolution_high = 0.0):

    fout = open(xds_inp, 'w')

    template = os.path.join(os.environ['FAST_DP_ROOT'],
                            'lib', 'templates',
                            '%s_CORRECT.INP' % metadata['detector'])

    template = os.path.join(os.environ['FAST_DP_ROOT'],
                            'lib', 'templates',
                            '%s_CORRECT_NO_CELL.INP' % metadata['detector'])

    if not os.path.exists(template):
        raise RuntimeError, 'template for %s not found at %s' % \
              (metadata['detector'], template)

    template_str = open(template, 'r').read().strip()

    # should somehow hang this from an anomalous flag

    friedels_law = 'FALSE'

    if scale:
        corrections = 'ALL'
    else:
        corrections = '!'

    fout.write('%s\n' % template_str.format(
        no_processors = get_number_cpus(),
        resolution_low = resolution_low,
        resolution_high = resolution_high,
        nx = metadata['size'][0],
        ny = metadata['size'][1],
        qx = metadata['pixel'][0],
        qy = metadata['pixel'][1],
        orgx = metadata['beam'][1] / metadata['pixel'][1],
        orgy = metadata['beam'][0] / metadata['pixel'][0],
        distance = metadata['distance'],
        sensor = metadata['sensor'],
        wavelength = metadata['wavelength'],
        oscillation = metadata['oscillation'][1],
        friedels_law = friedels_law,
        corrections = corrections,
        template = os.path.join(metadata['directory'],
                                metadata['template'].replace('#', '?')),
        starting_angle = metadata['oscillation'][0],
        starting_image = metadata['start']))

    # then we get the non-template stuff

    fout.write('DATA_RANGE=%d %d\n' % (metadata['start'],
                                       metadata['end']))

    fout.close()

    return