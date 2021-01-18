from PIL import Image, ImageDraw

image = Image.new('RGB', (200,200), color='white')


def draw_icon(xy, box_size, icon, rotation = None):
  """Custom function to add icons of weather font on image
  image = on which image should the text be added?
  xy = xy-coordinates as tuple -> (x,y)
  box_size = size of text-box -> (width,height)
  icon = icon-unicode, looks this up in weathericons dictionary
  """
  x,y = xy
  box_width, box_height = box_size
  text = icon
  font = self.weatherfont

  # Increase fontsize to fit specified height and width of text box
  size = 8
  font = ImageFont.truetype(font.path, size)
  #text_width, text_height = font.getsize(text)
  
  text_width = font.getsize(text)[0]
  ascent = font.getmetrics()[0]
  (width, baseline), (offset_x, offset_y) = font.font.getsize(text)
  text_height = ascent - offset_y      
  
  while (text_width < int(box_width * 0.9) and
         text_height < int(box_height * 0.9)):
    size += 1
    font = ImageFont.truetype(font.path, size)
    text_width, text_height = font.getsize(text)

  text_width, text_height = font.getsize(text)

  # Align text to desired position
  x = int((box_width / 2) - (text_width / 2))
  y = int((box_height / 2) - (text_height / 2))

  # Draw the text in the text-box
  draw  = ImageDraw.Draw(image)
  space = Image.new('RGBA', (box_width, box_height))
  ImageDraw.Draw(space).text((x, y), text, fill='black', font=font)

  if rotation != None:
    space.rotate(rotation, expand = True)

  # Update only region with text (add text with transparent background)
  image.paste(space, xy, space)
