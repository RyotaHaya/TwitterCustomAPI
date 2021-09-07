import numpy as np
import cv2
import requests

class IdentifiResult:
    # 
    media_type: str
    score: np.double
    media_source: str

def create_canny_img(gray_img_src, origin_img_src):
    """create 3 Mat from a image_file.
    argument:
        img_name (str): image file's name
    return:
        can_img (Mat):Edge detecion by canny
        gau_can_img (Mat): Edge detection by canny after GaussianBlur
        med_can_img (Mat): Edge detection by canny agter MedianBlur
    """
    ave_square = (5, 5)
    # x軸方向の標準偏差
    sigma_x = 1
    if type(origin_img_src[0][0]) == np.ndarray:
        gray_img_src = cv2.cvtColor(gray_img_src, cv2.COLOR_BGR2GRAY)
    can_img = cv2.Canny(gray_img_src, 100, 200)

    gau_img = cv2.GaussianBlur(gray_img_src, ave_square, sigma_x)
    gau_can_img = cv2.Canny(gau_img, 100, 200)

    med_img = cv2.medianBlur(gray_img_src, ksize=5)

    med_can_img = cv2.Canny(med_img, 100, 200)

    return can_img, gau_can_img, med_can_img

def get_color(img_src):
    """
    argument:
        img_name (str): file name

    return:
        result (float): maxium value of the most used color
    """

    same_colors = {}
    if type(img_src[0][0]) == np.ndarray:
        for row in img_src:
            for at in row:
                at = tuple(at)
                if at in same_colors:
                    same_colors[at] += 1
                else:
                    same_colors[at] = 0
    else:
        for row in img_src:
            for at in row:
                if at in same_colors:
                    same_colors[at] += 1
                else:
                    same_colors[at] = 0

    result = max(same_colors.values()) / len(img_src)

    return result

def cal_diff(mat, c_mat):
    """
    argument:
        mat (Mat):
        c_mat:

    return:
        result (float): mat diff
    """
    sum_mat = 0
    for m in mat:
        for n in m:
            sum_mat += n
    sum_mat /= 255
    diff = mat - c_mat
    sum_diff = 0
    for d in diff:
        for n in d:
            sum_diff += n
    sum_diff /= 255
    result = sum_diff / sum_mat

    return result

def cal_score(gau_result, med_result, color_result):
    result1 = gau_result + med_result
    return ((1 / result1) * 0.8 + (color_result / 100) * 0.2) * 0.625

def resize_img(img_name):
    img_src = cv2.imread(img_name, cv2.IMREAD_UNCHANGED)

    if len(img_src) > 2000 or len(img_src[0]) > 2000:
        img_src = cv2.resize(img_src,(len(img_src) // 2, len(img_src[0]) // 2))

    return img_src

def identifies_img(media_url):
    result = IdentifiResult()
    result.media_source = media_url
    
    img_src = imread_web(media_url)

    temp_img_src = img_src
    can_img, gau_can_img, med_can_img = create_canny_img(img_src,temp_img_src)
    gau_result = cal_diff(can_img, gau_can_img)
    med_result = cal_diff(can_img, med_can_img)
    color_result = get_color(img_src)
    score = cal_score(gau_result, med_result, color_result)

    print("socore = " + str(score))
    if score >= 0.5:
        result.media_type ="illust"
    else:
        result.media_type ="photo"

    result.score = score
    return result

def imread_web(url):
    # 画像をリクエストする
    resp= requests.get(url, stream=True).raw
    image= np.asarray(bytearray(resp.read()), dtype="uint8")
    image= cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

#関数で呼び出しする場合
def do_identifiesImage(media_url):

    ret = identifies_img(media_url)
    if ret.media_type == "illust":
        print("is illuts")
        return True
    else :
        print("not illuts")
        return False




