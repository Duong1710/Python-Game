import os
import pygame                      
from settings import *             
from pygame.math import Vector2 as vector 

# Định nghĩa lớp Player
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, path, collision_sprites):
        super().__init__(group)    # Khởi tạo lớp cơ sở (Sprite) và thêm player vào nhóm sprite `group` được truyền vào

        self.import_assets(path)               # Lấy asset cho player tại path(đường dẫn)
        self.frame_index = 0
        self.status = 'right'
        self.image = self.animations[self.status][self.frame_index]             

        self.rect = self.image.get_rect(topleft=pos)  # Tạo hình chữ nhật (rect) bao quanh `image` và đặt góc trên cùng bên trái tại vị trí `pos`

        self.z = LAYER['main']                 # Layer nhân vật sẽ tồn tại
        self.direction = vector()              # Vector2 để quản lý hướng di chuyển của nhân vật
        self.pos = vector(self.rect.topleft)   # Sao chép vị trí ban đầu của `rect` vào `pos` dưới dạng vector để xử lý di chuyển chính xác hơn      
        self.speed = 400                       # Đặt tốc độ di chuyển của nhân vật (400 pixel mỗi giây  

        #Collisions
        self.old_rect = self.rect.copy()        # Lưu trữ vị trí hiện tại của player 
        self.collision_sprites = collision_sprites  

        #Vertical movement
        self.gravity = 15
        self.jump_speed = 1200
        self.on_floor = False
        self.duck = False

    def import_assets(self, path):
        self.animations = {}  # Tạo một từ điển trống để lưu các animation theo từng tên thư mục.
    
        # Duyệt qua tất cả các thư mục con và tệp trong thư mục 'path' bằng os.walk
        for index, (root, dirs, files) in enumerate(os.walk(path)):
            # Nếu là vòng lặp đầu tiên (index == 0), ta đang ở thư mục gốc
            if index == 0:
                # Thêm mỗi thư mục con trong 'dirs' làm một khóa trong từ điển animations và khởi tạo một danh sách trống để chứa các bề mặt (Surface) tương ứng
                for name in dirs:
                    self.animations[name] = []
            else:
                # Lấy tên thư mục hiện tại từ biến root (tên thư mục chứa các tệp ảnh)
                key = os.path.basename(root)  
            
                # Sắp xếp danh sách các tệp ảnh trong thư mục hiện tại theo thứ tự số nếu có
                # (Dùng split('.')[0] để lấy phần trước dấu chấm)
                sorted_files = sorted(files, key=lambda string: int(string.split('.')[0]))
            
                # Duyệt qua từng tệp đã được sắp xếp trong thư mục hiện tại
                for file_name in sorted_files:
                    # Tạo đường dẫn đầy đủ đến tệp bằng os.path.join, sau đó chuẩn hóa dấu gạch chéo
                    full_path = os.path.join(root, file_name).replace('\\', '/')
                
                    # Tải tệp ảnh lên dưới dạng bề mặt (Surface) của pygame, sử dụng convert_alpha để hỗ trợ ảnh trong suốt
                    surf = pygame.image.load(full_path).convert_alpha()
                
                    # Thêm Surface đã tải vào danh sách của thư mục tương ứng trong self.animations
                    self.animations[key].append(surf)

        # In ra toàn bộ từ điển animations để kiểm tra dữ liệu đã tải
        print(self.animations)

    def animate(self, dt):                      # Hàm tạo animate
        self.frame_index += 7 * dt              # Tốc độ lặp animation            
        current_animations = self.animations[self.status]   
        if self.frame_index >= len(current_animations):   # Lặp lại từ đầu nếu đã tới frame cuối
            self.frame_index = 0
        
        self.image = current_animations[int(self.frame_index)]  # Lấy image của frame hiện tại


    def input(self):
        # Nhận input người dùng để xác định hướng di chuyển
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:                  
            self.direction.x = 1
        elif keys[pygame.K_a]:                 
            self.direction.x = -1
        else:
            self.direction.x = 0              

        if keys[pygame.K_w] and self.on_floor:
            self.direction.y = -self.jump_speed

        if keys[pygame.K_s]:
            self.duck = True
        else:
            self.duck = False          

    def move(self, dt):
        # Tính toán vị trí mới dựa trên hướng di chuyển, tốc độ và thời gian giữa các khung hình
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)        # Cập nhật vị trí x của `rect` với giá trị x mới đã được làm tròn
        self.collision('horizontal')           # Kiểm tra collison horizontal axit

        self.direction.y += self.gravity
        self.pos.y += self.direction.y * dt
        self.rect.y = round(self.pos.y)        # Cập nhật vị trí y của `rect` với giá trị y mới đã được làm tròn
        self.collision('vertical')             # Kiểm tra collison vertical axit

    def collision(self, direction):             # Kiểm tra các điều kiện collision
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):    

                if direction == 'horizontal':   # Collision theo horizontal axis
                    # Left collison
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:  # Kiểm tra hướng va chạm(Trạng thái trước va chạm)
                        self.rect.left = sprite.rect.right
                    # Right collison
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:  # Kiểm tra hướng va chạm
                        self.rect.right = sprite.rect.left
                    self.pos.x = self.rect.x    # Cập nhật vị trí mới
                else:                           # Collision theo vertical axis
                    # Bottom collison
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.on_floor = True
                    # Top collison
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                    self.pos.y = self.rect.y
                    self.direction.y = 0        # Khi va chạm theo chiều dọc, dừng chuyển động dọc (y) của nhân vật   

        if self.on_floor and self.direction.y != 0:
            self.on_floor = False
        
    def update(self, dt):
        self.old_rect = self.rect.copy()       # Cập nhật liên tục trạng thái của player
        self.input()                           
        self.move(dt)   
        self.animate(dt)                      
