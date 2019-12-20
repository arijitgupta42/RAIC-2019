import model


class MyStrategy:
	def __init__(self):
		pass

	def get_action(self, unit, game, debug):
		swap_weapon=False
		shoot = False
		velocity = 0
		jump = False
		jump_down = False
		mindist = 15
		rload = False
		plant_mine = False
		need_health = False
		aim = model.Vec2Double(0,0)
		target_pos = unit.position
		time_passed = game.current_tick

		def circle(a, b, r):
			return (a.x - b.x) ** 2 + (a.y -b.y) ** 2 <= r ** 2 

		def distance_sqr(a, b):
			return int(a.x - b.x) ** 2 + int(a.y - b.y) ** 2
		nearest_enemy = min(
			filter(lambda u: u.player_id != unit.player_id, game.units),
			key=lambda u: distance_sqr(u.position, unit.position),
			default=None)
		nearest_health = min(
			filter(lambda box: isinstance(
				box.item, model.Item.HealthPack), game.loot_boxes),
			key=lambda box: distance_sqr(box.position, unit.position),
			default=None)
		
		nearest_arm = min(
			filter(lambda box: isinstance(
				box.item, model.Item.Weapon), game.loot_boxes),
			key=lambda box: distance_sqr(box.position, unit.position),
			default=None)
		
		nearest_wep = min(
		filter(lambda box: box.item.weapon_type.value == 2, filter(lambda weapon: weapon.item.TAG == 1, game.loot_boxes)),
		key = lambda box: distance_sqr(box.position, unit.position),
		default = None)

		nearest_weapon = min(
		filter(lambda box: box.item.weapon_type.value == 0, filter(lambda weapon: weapon.item.TAG == 1, game.loot_boxes)),
		key = lambda box: distance_sqr(box.position, unit.position),
		default = None)

		health = []
		for box in game.loot_boxes:
			if box.item.TAG == 0:
				health.append(box.position)
		for i in range(1, len(health)): 
			key = health[i].x 
			j = i-1
			while j >=0 and key < health[j].x : 
					health[j+1].x = health[j].x 
					j -= 1
			health[j+1].x = key 
		print(health)

		enemies =[]
		for bot in game.units:
			if bot.player_id != unit.player_id:
				enemies.append(bot)
		
		bots =[]
		for bot in game.units:
			if bot.player_id == unit.player_id:
				bots.append(bot)
		if enemies[0].position.x > bots[0].position.x and time_passed < 10:
			for i in range(1, len(bots)): 
				key = bots[i].position.x 
				j = i-1
				while j >=0 and key < bots[j].position.x : 
						bots[j+1].position.x = bots[j].position.x 
						j -= 1
				bots[j+1].position.x = key 

		elif enemies[0].position.x > bots[0].position.x and time_passed < 10:
			for i in range(1, len(bots)): 
				key = bots[i].position.x 
				j = i-1
				while j >=0 and key < bots[j].position.x : 
						bots[j+1].position.x = bots[j].position.x 
						j -= 1
				bots[j+1].position.x = key 
			bots.reverse()
			
		if time_passed < 10:
			if bots[0].weapon is not None and bots[0].weapon.params.explosion is not None:
				bots.reverse()
			elif len(bots) == 2 and bots[1].weapon is not None and bots[1].weapon.params.explosion is None:
				bots.reverse()
			
		def line_of_sight(unit, enemy):
				if unit.x > enemy.x:
					for x in range(int(unit.x), int(enemy.x),-1):
						y = ((enemy.y-unit.y)/(enemy.x-unit.x))*(x-unit.x) + unit.y 
						try:
							if(game.level.tiles[int(x)][int(y)] == model.Tile.WALL):
								return False
						except:
							return True
				else:
					for x in range(int(unit.x), int(enemy.x)):
						y = ((enemy.y-unit.y)/(enemy.x-unit.x))*(x-unit.x) + unit.y 
						try:
							if(game.level.tiles[int(x)][int(y)] == model.Tile.WALL):
								return False
						except:
							return True
				return True
		debug.draw(model.CustomData.Log("Target pos: {}".format(target_pos)))
		debug.draw(model.CustomData.Log("Time Passed: {}".format(time_passed)))

		if unit.weapon is None and nearest_weapon is not None and unit.id == bots[0].id:
			target_pos = nearest_weapon.position
			aim = model.Vec2Double(int(target_pos.x - unit.position.x),int(target_pos.y - unit.position.y))
			jump = target_pos.y > unit.position.y
		
			if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True
			elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True

			if target_pos.x != unit.position.x:
				velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))

			jump_down = not jump

			try:
				if velocity > 0 and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y) - 1] == model.Tile.WALL:
					jump = True
					jump_down = False
				if velocity < 0 and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y) - 1] == model.Tile.WALL:
					jump = True
					jump_down = False
			except:
				print("sad")

			if jump_down:
				if game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 1] == model.Tile.JUMP_PAD or game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 2] == model.Tile.JUMP_PAD:
					if target_pos.x > unit.position.x:
						velocity = game.properties.unit_max_horizontal_speed
					else:
						velocity = -game.properties.unit_max_horizontal_speed


		if unit.weapon is None and nearest_wep is not None and len(bots) == 2 and unit.id == bots[1].id:
			target_pos = nearest_wep.position
			aim = model.Vec2Double(int(target_pos.x - unit.position.x),int(target_pos.y - unit.position.y))
			jump = target_pos.y > unit.position.y
		
			if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True
			elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True

			if target_pos.x != unit.position.x:
				velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))

			jump_down = not jump

			try:
				if velocity > 0 and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y) - 1] == model.Tile.WALL and game.level.tiles[int(unit.position.x + 2)][int(unit.position.y) - 1] == model.Tile.WALL and game.level.tiles[int(unit.position.x + 3)][int(unit.position.y) - 1] == model.Tile.WALL:
					jump = True
					jump_down = False
				if velocity < 0 and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y) - 1] == model.Tile.WALL and game.level.tiles[int(unit.position.x - 2)][int(unit.position.y) - 1] == model.Tile.WALL and game.level.tiles[int(unit.position.x - 3)][int(unit.position.y) - 1] == model.Tile.WALL:
					jump = True
					jump_down = False
			except:
				print("sad")

			if jump_down:
				if game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 1] == model.Tile.JUMP_PAD or game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 2] == model.Tile.JUMP_PAD:
					if target_pos.x > unit.position.x:
						velocity = game.properties.unit_max_horizontal_speed
					elif game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 1] == model.Tile.JUMP_PAD or game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 2] == model.Tile.JUMP_PAD:
						velocity = -game.properties.unit_max_horizontal_speed
		
		if unit.weapon is not None and unit.weapon.typ.value != 0 and nearest_weapon is not None and unit.id == bots[0].id:
			swap_weapon = True
			target_pos = nearest_weapon.position
			aim = model.Vec2Double(int(target_pos.x - unit.position.x),int(target_pos.y - unit.position.y))
			jump = target_pos.y > unit.position.y			

			if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True
			elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True

			if target_pos.x != unit.position.x:
				velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))

			jump_down = not jump

			if jump_down:
				if game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 1] == model.Tile.JUMP_PAD or game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 2] == model.Tile.JUMP_PAD:
					if target_pos.x > unit.position.x:
						velocity = game.properties.unit_max_horizontal_speed
					elif game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 1] == model.Tile.JUMP_PAD or game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 2] == model.Tile.JUMP_PAD:
						velocity = -game.properties.unit_max_horizontal_speed
			if nearest_enemy is not None:
				
				aim = model.Vec2Double((nearest_enemy.position.x - unit.position.x),(nearest_enemy.position.y - unit.position.y) + 0.15)
				if line_of_sight(unit.position, nearest_enemy.position):
					shoot = True

		elif unit.weapon is None and nearest_wep is None and nearest_arm is not None and len(bots) == 2 and unit.id == bots[1].id:
			swap_weapon = True
			target_pos = nearest_arm.position
			aim = model.Vec2Double(int(target_pos.x - unit.position.x),int(target_pos.y - unit.position.y))
			jump = target_pos.y > unit.position.y			

			if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True
			elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True

			if target_pos.x != unit.position.x:
				velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))

			jump_down = not jump

			if jump_down:
				if game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 1] == model.Tile.JUMP_PAD or game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 2] == model.Tile.JUMP_PAD:
					if target_pos.x > unit.position.x:
						velocity = game.properties.unit_max_horizontal_speed
					elif game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 1] == model.Tile.JUMP_PAD or game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 2] == model.Tile.JUMP_PAD:
						velocity = -game.properties.unit_max_horizontal_speed

			if nearest_enemy is not None:
				
				aim = model.Vec2Double((nearest_enemy.position.x - unit.position.x),(nearest_enemy.position.y - unit.position.y) + 0.15)
				if line_of_sight(unit.position, nearest_enemy.position):
					shoot = True


		elif unit.weapon is not None and unit.weapon.typ.value != 2 and nearest_wep is not None and len(bots) == 2 and unit.id == bots[1].id:
			swap_weapon = True
			try:
				if distance_sqr(unit.position, nearest_weapon) < 1.1:
					swap_weapon = False
			except:
				swap_weapon = True
			target_pos = nearest_wep.position
			aim = model.Vec2Double(int(target_pos.x - unit.position.x),int(target_pos.y - unit.position.y))
			jump = target_pos.y > unit.position.y			

			if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True
			elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
				jump = True

			if target_pos.x != unit.position.x:
				velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))

			jump_down = not jump

			if jump_down:
				if game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 1] == model.Tile.JUMP_PAD or game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 2] == model.Tile.JUMP_PAD:
					if target_pos.x > unit.position.x:
						velocity = game.properties.unit_max_horizontal_speed
					elif game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 1] == model.Tile.JUMP_PAD or game.level.tiles[int(unit.position.x) + 1][int(unit.position.y) - 2] == model.Tile.JUMP_PAD:
						velocity = -game.properties.unit_max_horizontal_speed

			if nearest_enemy is not None:
				
				aim = model.Vec2Double((nearest_enemy.position.x - unit.position.x),(nearest_enemy.position.y - unit.position.y) + 0.15)
				if line_of_sight(unit.position, nearest_enemy.position):
					shoot = True

				
		else:
			if unit.weapon is not None and nearest_enemy is not None:
				target_pos = nearest_enemy.position
				aim = model.Vec2Double((target_pos.x - unit.position.x),(target_pos.y - unit.position.y) + 0.15)
				
				if nearest_enemy.weapon is not None:
					if nearest_enemy.weapon.fire_timer is not None:
						if nearest_enemy.weapon.fire_timer > 0.4 and line_of_sight(unit.position, nearest_enemy.position):
							shoot = True
							if nearest_enemy.health < unit.health:
								mindist = 4/(1 + ((nearest_enemy.health - unit.health)*0.25)*0.5) 
							else:
								mindist = 2

							jump = target_pos.y > unit.position.y
					
							if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
								jump = True
							elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
								jump = True

							if target_pos.x != unit.position.x:
								try:
									velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))
								except:
									velocity = game.properties.unit_max_horizontal_speed
							jump_down = not jump

							
							if unit.position.x == nearest_enemy.position.x - mindist or unit.position.x == nearest_enemy.position.x + mindist:
								velocity = 0
							
							if unit.position.y == nearest_enemy.position.y + (2*mindist) or unit.position.y == nearest_enemy.position.y - (2*mindist):
								jump = False
								jump_down = False

					elif nearest_enemy.weapon.fire_timer is None and line_of_sight(unit.position, nearest_enemy.position):
						shoot = True 
						if nearest_enemy.health < unit.health:
							mindist = 4/(1 + ((nearest_enemy.health - unit.health)*0.25)*0.5) 
						else:
							mindist = 4
						jump = target_pos.y > unit.position.y
				
						if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
							jump = True
						elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
							jump = True

						if target_pos.x != unit.position.x:
							try:
								velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))
							except:
								velocity = game.properties.unit_max_horizontal_speed
						jump_down = not jump
							
						if unit.position.x == nearest_enemy.position.x - mindist or unit.position.x == nearest_enemy.position.x + mindist:
							velocity = 0
						
						if unit.position.y == nearest_enemy.position.y + (2*mindist) or unit.position.y == nearest_enemy.position.y - (2*mindist):
							jump = False
							jump_down = False
	
				if distance_sqr(nearest_enemy.position, unit.position) <= 16 and line_of_sight(unit.position, nearest_enemy.position):
					shoot = True
				
				if nearest_enemy.weapon is None and line_of_sight(unit.position, nearest_enemy.position):
					shoot = True
				
				if line_of_sight(unit.position, nearest_enemy.position):
					
					if len(bots) == 2:
						if unit.weapon.params.explosion is None:
							if nearest_enemy.health < unit.health and bots[1].health < (game.properties.unit_max_health)*0.5:
								mindist = 14/(1 + ((nearest_enemy.health - unit.health)*0.25)*0.5)  
							else:
								mindist = 14
							if distance_sqr(nearest_enemy.position, unit.position) <= 144 and line_of_sight(unit.position, nearest_enemy.position):
								shoot = True
						else:
							if nearest_enemy.health < unit.health:
								mindist = 4/(1 + ((nearest_enemy.health - unit.health)*0.25)*0.5) 
							else:
								mindist = 4
					
					else:
						if mindist == 15:
							if nearest_enemy.health < unit.health and unit.weapon.magazine < unit.weapon.params.magazine_size and nearest_enemy.weapon is not None and nearest_enemy.weapon.fire_timer is not None and unit.weapon.fire_timer is not None and unit.weapon.fire_timer > nearest_enemy.weapon.fire_timer:
								mindist = 10/(1 + ((nearest_enemy.health - unit.health)*0.25)*0.5) 
							else:
								mindist = 10

					if nearest_enemy.weapon is not None and nearest_enemy.weapon.params.explosion is not None:
						mindist += 4

					if int(nearest_enemy.position.x - mindist)< int(unit.position.x)< int(nearest_enemy.position.x + mindist):
						try:
							velocity = -game.properties.unit_max_horizontal_speed * (int(target_pos.x) - int(unit.position.x))/abs(int(target_pos.x) - int(unit.position.x))
						except:
							if game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
								velocity = -game.properties.unit_max_horizontal_speed
							else:
								velocity = game.properties.unit_max_horizontal_speed
						if unit.weapon.params.explosion is not None:
							if distance_sqr(nearest_enemy.position, unit.position) <= 4:
								plant_mine = True

					else:
						try:
							velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))
						except:
							if game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
								velocity = -game.properties.unit_max_horizontal_speed
							else:
								velocity = game.properties.unit_max_horizontal_speed
					
					if int(nearest_enemy.position.y - (2*mindist))< int(unit.position.y)< int(nearest_enemy.position.y + (2*mindist)):
						jump = target_pos.y < unit.position.y
						jump_down = not jump
					elif unit.position.y == nearest_enemy.position.y + (2*mindist) or unit.position.y == nearest_enemy.position.y - (2*mindist):
						jump = False
						jump_down = False
					else:
						jump = target_pos.y > unit.position.y
						jump_down = not jump

					if velocity > 0 and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True
						jump_down = False
						if int(unit.position.x) == 38:
							velocity = - velocity
					elif velocity < 0 and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True
						jump_down = False
						if int(unit.position.x) == 0:
							velocity = -velocity

				else:
					if len(bots) == 2:
						if unit.weapon.params.explosion is None:
							if nearest_enemy.health < unit.health and bots[1].health < (game.properties.unit_max_health)*0.5:
								mindist = 14/(1 + ((nearest_enemy.health - unit.health)*0.25)*0.5) 
							else:
								mindist = 14
						else:
							if nearest_enemy.health < unit.health:
								mindist = 4/(1 + ((nearest_enemy.health - unit.health)*0.25)*0.5) 
							else:
								mindist = 4
					
					else:
						if mindist == 15:
							if nearest_enemy.health < unit.health and unit.weapon.magazine < unit.weapon.params.magazine_size and nearest_enemy.weapon is not None and nearest_enemy.weapon.fire_timer is not None and unit.weapon.fire_timer is not None and unit.weapon.fire_timer > nearest_enemy.weapon.fire_timer:
								mindist = 10/(1 + ((nearest_enemy.health - unit.health)*0.25)*0.5) 
							else:
								mindist = 10
							
					jump = target_pos.y > unit.position.y
			
					if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True
					elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True

					if target_pos.x != unit.position.x:
						try:
							velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))
						except:
							if game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
								velocity = -game.properties.unit_max_horizontal_speed
							else:
								velocity = game.properties.unit_max_horizontal_speed

					if distance_sqr(target_pos, unit.position) < mindist:
						velocity = -velocity
						jump = not jump

					jump_down = not jump

					if unit.position.x == nearest_enemy.position.x - mindist or unit.position.x == nearest_enemy.position.x + mindist:
						velocity = 0
					
					if unit.position.y == nearest_enemy.position.y + (2*mindist) or unit.position.y == nearest_enemy.position.y - (2*mindist):
						jump = False
						jump_down = False


			if time_passed > 3000 and nearest_enemy.health >= unit.health and shoot is False:
					jump = target_pos.y > unit.position.y

					if target_pos.x > unit.position.x and nearest_enemy.position.x > unit.position.x:
						jump = True
					elif target_pos.x < unit.position.x and nearest_enemy.position.x < unit.position.x:
						jump = True
									
					if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True
					elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True

					if target_pos.x != unit.position.x:
						try:
							velocity=unit.weapon.params.bullet.speed * 0.6 * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))
						except:
							velocity = game.properties.unit_max_horizontal_speed
					jump_down = not jump


			if time_passed > 3300 and nearest_enemy.health >= unit.health:
					jump = target_pos.y > unit.position.y

					if target_pos.x > unit.position.x and nearest_enemy.position.x > unit.position.x:
						jump = True
					elif target_pos.x < unit.position.x and nearest_enemy.position.x < unit.position.x:
						jump = True
									
					if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True
					elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True

					if target_pos.x != unit.position.x:
						try:
							velocity=unit.weapon.params.bullet.speed * 0.6 * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))
						except:
							velocity = game.properties.unit_max_horizontal_speed
					jump_down = not jump
			
			
			if unit.jump_state.can_cancel is True and unit.jump_state.max_time < 0.32 and game.level.tiles[int(unit.position.x)][int(unit.position.y) - 2] == model.Tile.PLATFORM and unit.health >= (game.properties.unit_max_health)*0.775:
				jump = False
				jump_down = True
			
			h_right = None
			h_left = None

			if unit.weapon is not None and nearest_health is not None and unit.health < (game.properties.unit_max_health)*0.775:
				if len(health) == 1:
					target_pos = nearest_health.position
				
				
				elif len(health) >1:

					if unit.position.x < health[0].x:
						target_pos = health[0]
					elif unit.position.x > health[-1].x:
						target_pos = health[-1]
					else:
						for i in range(1, len(health)):
							if health[i].x > unit.position.x:
								h_right = health[i]
								h_left = health[i-1]
						if int(nearest_enemy.position.x) > int(unit.position.x):
							target_pos = h_left
						elif int(nearest_enemy.position.x) < int(unit.position.x):
							target_pos = h_right
						else:
							if game.level.tiles[int(unit.position.x) + 1][int(unit.position.y)] == model.Tile.WALL:
								target_pos = h_left
							elif game.level.tiles[int(unit.position.x) - 1][int(unit.position.y)] == model.Tile.WALL:
								target_pos = h_right
							else:
								target_pos = h_right

				if unit.health < game.properties.unit_max_health*0.25:
					need_health = True

				aim = model.Vec2Double((nearest_enemy.position.x - unit.position.x),(nearest_enemy.position.y - unit.position.y + 0.15))
				jump = target_pos.y > unit.position.y
			
				if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
					jump = True
				elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
					jump = True

				if target_pos.x != unit.position.x:
					velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))

				jump_down = not jump

				if unit.jump_state.can_cancel is True and unit.jump_state.max_time < 0.3 and game.level.tiles[int(unit.position.x)][int(unit.position.y) - 2] == model.Tile.PLATFORM:
					jump = False
					jump_down = True

				if target_pos.x > unit.position.x and nearest_enemy.position.x > unit.position.x:
					jump_down = unit.jump_state.max_time < 0.3
					jump = not jump_down
				elif target_pos.x < unit.position.x and nearest_enemy.position.x < unit.position.x:
					jump_down = unit.jump_state.max_time < 0.3
					jump = not jump_down

				if nearest_enemy.weapon is not None:
					if nearest_enemy.weapon.fire_timer is not None:
						if nearest_enemy.weapon.fire_timer > 0.4 and line_of_sight(unit.position, nearest_enemy.position):
							shoot = True
					elif nearest_enemy.weapon.fire_timer is None and line_of_sight(unit.position, nearest_enemy.position):
						shoot = True 
				if distance_sqr(nearest_enemy.position, unit.position) <= 25 and line_of_sight(unit.position, nearest_enemy.position):
					shoot = True
				if nearest_enemy.weapon is None and line_of_sight(unit.position, nearest_enemy.position):
					shoot = True

			if unit.weapon is not None and unit.health < game.properties.unit_max_health*0.2 and nearest_enemy is not None and nearest_enemy.health < game.properties.unit_max_health*0.4 and nearest_health is None:
				if nearest_wep is not None:
					target_pos = nearest_wep.position
					aim = model.Vec2Double((nearest_enemy.position.x - unit.position.x),(nearest_enemy.position.y - unit.position.y + 0.15))
					jump = target_pos.y > unit.position.y
				
					if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True
					elif target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
						jump = True

					if target_pos.x != unit.position.x:
						velocity = game.properties.unit_max_horizontal_speed * ((target_pos.x - unit.position.x)/abs(target_pos.x - unit.position.x))

					jump_down = not jump

					if unit.jump_state.can_cancel is True and unit.jump_state.max_time < 0.3 and game.level.tiles[int(unit.position.x)][int(unit.position.y) - 2] == model.Tile.PLATFORM:
						jump = False
						jump_down = True

					if target_pos.x > unit.position.x and nearest_enemy.position.x > unit.position.x:
						jump = True
						jump_down = unit.jump_state.max_time < 0.3
					elif target_pos.x < unit.position.x and nearest_enemy.position.x < unit.position.x:
						jump = True
						jump_down = unit.jump_state.max_time < 0.3
									

					if nearest_enemy.weapon is not None:
						if nearest_enemy.weapon.fire_timer is not None:
							if nearest_enemy.weapon.fire_timer > 0.4 and line_of_sight(unit.position, nearest_enemy.position):
								shoot = True
						elif nearest_enemy.weapon.fire_timer is None and line_of_sight(unit.position, nearest_enemy.position):
							shoot = True 
					if distance_sqr(nearest_enemy.position, unit.position) <= 16 and line_of_sight(unit.position, nearest_enemy.position):
						shoot = True
					if nearest_enemy.weapon is None and line_of_sight(unit.position, nearest_enemy.position):
						shoot = True	
			
			unit_centre = model.Vec2Double(unit.position.x, unit.position.y + 0.9 )
			if unit.weapon is not None and unit.weapon.params.explosion is not None and unit.health < game.properties.unit_max_health*0.2 and nearest_health is None:
				if shoot:
					if distance_sqr(nearest_enemy.position, unit.position) <= 2 and line_of_sight(nearest_enemy.position, unit_centre):
						shoot = True
					else:
						shoot = False


			
			detect = 0
			explosion = 0
			exploding_tile = model.Vec2Double(0,0)
			for bullet in game.bullets:
				if bullet.unit_id != unit.id:
					if bullet.explosion_params is not None:
							radius = bullet.explosion_params.radius + 8
							explosion = bullet.explosion_params.radius
					else:
						try:
							radius = distance_sqr(unit_centre, nearest_enemy.position)
							radius = radius**(0.5)
						except:
							radius = 10
					if radius < 0:
						radius = -radius

					if int(unit_centre.x - radius)<int(bullet.position.x)<int(unit_centre.x + radius) and int(unit_centre.y - radius)<int(bullet.position.y)<int(unit_centre.y + radius) and not need_health:
						if unit_centre.x > bullet.position.x:
							for x in range(int(unit_centre.x), int(bullet.position.x),-1):
								y = (bullet.velocity.y/bullet.velocity.x)*(x-unit_centre.x) + unit_centre.y 
								try:
									if(game.level.tiles[int(x)][int(y)] == model.Tile.WALL):
										detect -= 1
										if bullet.explosion_params is not None:
											exploding_tile.x = x
											exploding_tile.y = y
								except:
									detect += 1
						else:
							for x in range(int(unit_centre.x), int(bullet.position.x)):
								y = (bullet.velocity.y/bullet.velocity.x)*(x-unit_centre.x) + unit_centre.y 
								try:
									if(game.level.tiles[int(x)][int(y)] == model.Tile.WALL):
										detect -= 1
										if bullet.explosion_params is not None:
											exploding_tile.x = x
											exploding_tile.y = y
								except:
									detect += 1
						detect += 1
						if detect > 0 and (bullet.velocity.x*(unit_centre.x - bullet.position.x)) > 0:
							y = (bullet.velocity.y/bullet.velocity.x)*(unit_centre.x - bullet.position.x) + bullet.position.y
							x = ((y - bullet.position.y)/(bullet.velocity.y/bullet.velocity.x))  + bullet.position.x
							
							if y > unit_centre.y + 1.1 + explosion:
								print("overhead")
							elif y < unit_centre.y - 1.1 - explosion:
								print("underneath")
							else:
								slope_bullet = bullet.velocity.y/bullet.velocity.x
								slope_req = (-1) * (1/slope_bullet)
								velocity = game.properties.unit_max_horizontal_speed
								if slope_req < 0:
									if int(bullet.position.y) >= int(unit_centre.y):
										jump = False
										jump_down = True
										if game.level.tiles[int(unit.position.x)][int(unit.position.y) - 1] == model.Tile.WALL:
											if bullet.position.x > unit.position.x:
												velocity = -velocity
									else:
										if unit.jump_state.can_jump:
											jump = True
											jump_down = False
											velocity = -velocity
										
								if slope_req > 0:
									if int(bullet.position.y) >= int(unit_centre.y):
										jump = False
										jump_down = True
										if game.level.tiles[int(unit.position.x)][int(unit.position.y) - 1] == model.Tile.WALL:
											if bullet.position.x < unit.position.x:
												velocity = -velocity
									else:
										if unit.jump_state.can_jump:
											jump = True 
											jump_down = False
								
								
						else:
							print("no need to dodge")

						if exploding_tile.x - explosion<unit_centre.x < exploding_tile.x + explosion and exploding_tile.y - explosion<unit_centre.y < exploding_tile.y + explosion:
							velocity = -velocity
							if velocity == 0:
								velocity = game.properties.unit_max_horizontal_speed * ((unit.position.x - exploding_tile.x)/abs(unit.position.x - exploding_tile.x))
							jump = unit.position.y > exploding_tile.y
							jump_down = not jump
										

		for mine in game.mines:
			if circle(unit.position, mine.position,mine.trigger_radius) and mine.state != 0:
				shoot = False
				jump = True
				if velocity != 0:
					velocity = -velocity
				else:
					try:
						velocity = -1 * game.properties.unit_max_horizontal_speed * ((mine.position.x - unit.position.x)/abs(mine.position.x - unit.position.x)) 
					except:
						if game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
							velocity = -game.properties.unit_max_horizontal_speed
						else:
							velocity = game.properties.unit_max_horizontal_speed
		
		if shoot:
			if nearest_enemy.position.y < unit.position.y and abs(nearest_enemy.position.x - unit.position.x) <= 2 and abs(nearest_enemy.position.y - unit.position.y) >= 8:
				if game.level.tiles[int(unit.position.x)][int(unit.position.y) - 1] == model.Tile.WALL:
					if unit.weapon.params.explosion is not None:
						try:
							velocity = game.properties.unit_max_horizontal_speed * ((nearest_enemy.position.x - unit.position.x)/abs(nearest_enemy.position.x - unit.position.x))
							jump = True
						except:
							shoot = False

			if unit.weapon.params.explosion is not None:
				if len(bots) == 2:
					if circle(bots[0].position, nearest_enemy.position, unit.weapon.params.explosion.radius):
						shoot = False
					if circle(bots[0].position, unit.position, unit.weapon.params.explosion.radius) and bots[0].health > game.properties.unit_max_health*0.2 and nearest_health is not None and nearest_enemy is not None and not circle(nearest_enemy.position, unit.position, unit.weapon.params.explosion.radius):
						shoot = False
					if circle(bots[1].position, nearest_enemy.position, unit.weapon.params.explosion.radius):
						shoot = True
					if (nearest_enemy.position.x - bots[0].position.x)*(nearest_enemy.position.x - unit.position.x) > 0:
						if abs(nearest_enemy.position.x - bots[0].position.x) < abs(nearest_enemy.position.x - unit.position.x):
							if(bots[0].health > game.properties.unit_max_health*0.5):
								shoot = False
					
			if unit.weapon.params.explosion is None:
				if len(bots) == 2:
					if (target_pos.x - bots[1].position.x)*(target_pos.x - unit.position.x) > 0:
						if abs(target_pos.x - bots[1].position.x) < abs(target_pos.x - unit.position.x):
							if(bots[1].health > game.properties.unit_max_health*0.35):
								shoot = False

		
		if unit.id == bots[0].id and len(bots) == 2:
			if nearest_enemy is not None:
				if distance_sqr(unit.position, bots[1].position) <= 2:
					jump = True
					if game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
						velocity = -game.properties.unit_max_horizontal_speed
					elif game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
						velocity = game.properties.unit_max_horizontal_speed


		 
		return model.UnitAction(
			velocity = velocity,
			jump = jump,
			jump_down = jump_down,
			aim = aim,
			shoot = shoot,
			reload = False,
			swap_weapon = swap_weapon,
			plant_mine = plant_mine)
