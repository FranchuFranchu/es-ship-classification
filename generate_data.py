from endless_sky.datafile import DataFile
from json.encoder import JSONEncoder

from os import environ
from pathlib import Path

df = DataFile(Path(environ["ENDLESS_SKY_PATH"]) / Path("data/human/ships.txt"))

extra_cargo_per_outfit_space = 15 / 20
extra_outfit_per_cargo_space = 20 / 15
extra_bunks_per_outfit_space = 4 / 20
extra_bunks_per_cargo_space = extra_bunks_per_outfit_space * extra_outfit_per_cargo_space

outfit_space = 0
cargo_space = 0
bunks = 0

from dataclasses import dataclass
@dataclass
class ShipStats:
	name: str = ""
	sprite: str = ""
	outfit_space: int = 0
	cargo_space: int = 0
	weapon_capacity: int = 0
	engine_capacity: int = 0
	bunks: int = 0
	def __iadd__(self, other):
		for key in type(other).__annotations__.keys():
			if hasattr(self, key):
				settatr(self, key, getattr(other, key) + getattr(self, key))
	
	@classmethod
	def from_datanode(ShipStats, i):
		kwargs = {"name": i.tokens[1], "sprite": next(i.filter_first("sprite")).tokens[1]}
		
		attributes = next(i.filter_first("attributes"))
		
		
		for k in ("cargo space", "outfit space", "bunks", "weapon capacity", "engine capacity"):
			try:
				kwargs[k.replace(" ", "_")] = int(next(attributes.filter_first(k)).tokens[1])
			except StopIteration:
				pass
			
		return ShipStats(**kwargs)
	
	def relative(self):
		total = 0
		kwargs = {}
		for k, v in type(self).__annotations__.items():
			if v is int:
				total += getattr(self, k)

		for k, v in type(self).__annotations__.items():
			if v is int:
				kwargs[k] = getattr(self, k) / total
			else:
				kwargs[k] = getattr(self, k)
				
		return type(self)(**kwargs)
		
class MyEncoder(JSONEncoder):
	def default(self, o):
		return {k: getattr(o, k) for k in o.__class__.__annotations__.keys()}
ship_stats = {}

for i in df.root.filter_first("ship"):
	if len(i.tokens) == 2:
		ship_stats[i.tokens[1]] = ShipStats.from_datanode(i)
	else:
		# Variants are ignored, for now
		# print(ship_stats[i.tokens[1]])
		pass
		
with open("data.json", "w") as f:
	f.write(MyEncoder().encode(ship_stats))