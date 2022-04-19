from idr import connection
import numpy
from skimage.io import imshow
from PIL import Image
import ssl
from omero import client as om_client
from omero import rtypes
from omero import sys as om_sys
import getpass
from omero.gateway import BlitzGateway
from omero.util.script_utils import readFlimImageFile

# ssl._create_default_https_context = ssl._create_unverified_context
ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_NONE

# conn = connection('idr.openmicroscopy.org')
conn = connection('publicomero.bio.ed.ac.uk')

CLIENT = None
SESSION = None

# Retrieve pixels for images by IDs
PIXELS_BY_IMAGE_QUERY = "SELECT p FROM Pixels as p JOIN FETCH p.image JOIN FETCH p.pixelsType \
                     WHERE p.image.id in :iids"

IMAGES_BY_ID_QUERY = "select i from Image i where i.id in :iids"

def get_connection():
    global CLIENT, SESSION

    ice_config = "/dev/null"

    CLIENT = om_client(host='publicomero.bio.ed.ac.uk', port=4064,
                  args=["=".join(["--Ice.Config", ice_config]), "--omero.debug=1"])
    SESSION = CLIENT.createSession('jhay1', getpass.getpass())
    conn = BlitzGateway(client_obj=CLIENT)

    # Using secure connection.
    # By default, once we have logged in, data transfer is not encrypted
    # (faster)
    # To use a secure connection, call setSecure(True):
    conn.setSecure(False)
    return conn


def find_objects_by_query(query, params):
    global SESSION

    query_service = SESSION.getQueryService()
    # query = "select p from Project p left outer join fetch p.datasetLinks as links left outer join fetch links.child as dataset where p.id =:pid"

    objects = query_service.findAllByQuery(query, params)

    return objects


# adapted from https://github.com/ome/omero-guide-ilastik/blob/e9df8014515a8dbbfd87623a24564044d05d2224/notebooks/pixel_classification.ipynb
def load_numpy_array(image):
    pixels = image.getPrimaryPixels()
    size_z = image.getSizeZ()
    size_c = image.getSizeC()
    size_t = image.getSizeT()
    size_y = image.getSizeY()
    size_x = image.getSizeX()
    z, t, c = 0, 0, 0  # first plane of the image

    zct_list = []
    for t in range(size_t):
        for z in range(size_z):  # get the Z-stack
            for c in range(size_c):  # all channels
                zct_list.append((z, c, t))

    values = []
    # Load all the planes as YX numpy array
    planes = pixels.getPlanes(zct_list)
    j = 0
    k = 0
    tmp_c = []
    tmp_z = []
    s = "z:%s t:%s c:%s y:%s x:%s" % (size_z, size_t, size_c, size_y, size_x)
    print(s)
    # axis tzyxc
    print("Downloading image %s" % image.getName())
    for i, p in enumerate(planes):
        if k < size_z:
            if j < size_c:
                tmp_c.append(p)
                j = j + 1
            if j == size_c:
                # use dstack to have c at the end
                tmp_z.append(numpy.dstack(tmp_c))
                tmp_c = []
                j = 0
                k = k + 1
        if k == size_z:  # done with the stack
            values.append(numpy.stack(tmp_z))
            tmp_z = []
            k = 0

    return numpy.stack(values)


def save_image(conn, image, input_data):
    pixels = image.getPrimaryPixels()
    size_z = image.getSizeZ()
    size_c = image.getSizeC()
    size_t = image.getSizeT()
    size_y = image.getSizeY()
    size_x = image.getSizeX()
    z, t, c = 0, 0, 0  # first plane of the image

    zct_list = []
    for t in range(size_t):
        for z in range(size_z):  # get the Z-stack
            for c in range(size_c):  # all channels
                # zct_list.append((z, c, t))

                # im = Image.fromarray(input_data[t,z,:,:,c])
                # im.save('_'.join([str(t),str(z),str(c),image.getName()])+'.png')
                rgb_data = input_data[t,z,:,:,:]
                im = Image.fromarray(numpy.ascontiguousarray(rgb_data.transpose(0,1,2)), 'RGB')
                im.save('_'.join([str(t),str(z),image.getName()])+'.png')


def retrieve_image(conn, dataset_id, image_id):
    input_data = None

    images = conn.getObjects('Image', opts={'dataset': dataset_id, 'image':image_id})
    # image_ids = map(rtypes.rlong, [image_id])

    # params = om_sys.Parameters()
    # params.map = {'iids' : rtypes.rlist(image_ids)}
    # images = find_objects_by_query(PIXELS_BY_IMAGE_QUERY, params)
    # images = find_objects_by_query(IMAGES_BY_ID_QUERY, params)

    for image in images:
        if image.getId() == image_id:
            input_data = load_numpy_array(image)
             
            save_image(conn, image, input_data)

    return input_data

# see: https://idr.openmicroscopy.org/webclient/?show=image-9844380
# dataset_id = 10655
# image_id = 9844380

dataset_id = 96
image_id = 561

# conn = get_connection()

input_data = retrieve_image(conn, dataset_id, image_id)

print(input_data.shape)
# imshow(input_data[0,0,:,:,0])

conn.close()
