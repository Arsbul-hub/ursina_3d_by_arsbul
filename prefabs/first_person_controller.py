from ursina_ import *



class FirstPersonController(Entity):
    def __init__(self,radius, **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        super().__init__()
        self.speed = 5
        self.height = 2
        self.pusher = CollisionHandlerPusher()
        self.camera_pivot = Entity(parent=self, y=self.height)
        base.cTrav = CollisionTraverser()
        camera.parent = self.camera_pivot
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_duration = .5
        self.jumping = False
        self.air_time = 0
        self.shape = CollisionCapsule(0,0,0,0,0,0, radius)
        self.node_path = render.attachNewNode(CollisionNode('1'))
        self.node_path.node().addSolid(self.shape)
        self.pusher.addCollider(self.node_path,self.node_path)
        base.cTrav.addCollider(self.node_path,self.pusher)
        self.node_path.show()
        for key, value in kwargs.items():
            setattr(self, key ,value)
        self.h = 0
        self.setPos(1,20,20)
    def update(self):

        h,p,r = self.node_path.getHpr()
        #print(self.getHpr()[0])
        self.h += mouse.velocity[0] * self.mouse_sensitivity[1]
        #print(self.h)
        self.node_path.setHpr(-self.h,0,0)
        #print(self.mouse_sensitivity[0] )
        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(self.forward * (held_keys['w'] - held_keys['s'])+ self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        #feet_ray = raycast(self.position+Vec3(0,0.5,0), self.direction, ignore=(self,), distance=.5, debug=False)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, ignore=(self,), distance=.5, debug=False)
        #if not feet_ray.hit and not head_ray.hit:
            #self.position += self.direction * self.speed * time.dt
        if held_keys['w']:
            self.node_path.setZ(self.node_path,0.1)
        if held_keys['s']:
            self.node_path.setZ(self.node_path,-0.1)
        if held_keys['a']:
            self.node_path.setX(self.node_path,-0.1)
        if held_keys['d']:
            self.node_path.setX(self.node_path,0.1)

        self.setX(self.node_path.getX())
        self.setZ(self.node_path.getZ())
        #self.setY(self.node_path.getY())
        #print(self.getHpr())
        self.setHpr(self.node_path.getHpr())
        self.node_path.setY(self.getY()+1)

        feet_ray = raycast(self.position+Vec3(0,0.5,0), self.direction, ignore=(self,), distance=.5, debug=False)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, ignore=(self,), distance=.5, debug=False)
        if self.gravity:
            # gravity
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
            # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

            if ray.distance <= self.height+.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity


    def input(self, key):
        if key == 'space':
            self.jump()


    def jump(self):
        if not self.grounded:
            return


        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_duration, resolution=int(1//time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.jump_duration)


    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        # print('land')
        self.air_time = 0
        self.grounded = True


    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True


    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False




if __name__ == '__main__':
    from ursina_.prefabs.first_person_controller import FirstPersonController
    # window.vsync = False
    app = Ursina()
    # Sky(color=color.gray)
    ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100),collider="box")

    e = Entity(model='cube', scale=(1,1,1), x=2, y=0.5, rotation_y=45, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)
 
    e = Entity(model='cube', scale=(1,1,1), x=-2, y=1, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)
    #cTrav = CollisionTraverser()
    #pusher = CollisionHandlerPusher()

    player = FirstPersonController(y=2,radius=0.25, origin_y=-.5)

   # hill = Entity(model='sphere', position=(20,-0,10), scale=(25,25,25), collider='mesh', color=color.green)
    # from ursina.shaders import basic_lighting_shader

    # player.add_script(NoclipMode())
    app.run()
