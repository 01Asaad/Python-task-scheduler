from collections.abc import Callable, Iterable, Mapping
from datetime import datetime, timedelta
from random import randint
from typing import Any, List
from threading import Thread
import pickle
from time import sleep

from datetime import timedelta
paused=True
on_error =None
on_error_parameters = []

def parse_timedelta_from_string(input_string):
	# Initialize components with default values
	minutes = 0
	hours = 0
	seconds=0
	
	# Split the input string into parts based on 'm' and 'h'
	parts = input_string.split()
	
	for part in parts:
		if part.endswith('m'):
			minutes += int(part[:-1])
		elif part.endswith('h'):
			hours += int(part[:-1])
		elif part.endswith('s') :
			seconds += int(part[:-1])
	
	# Create a timedelta object using the extracted components
	return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def task_executer() :
	last_checked_date=datetime.now()
	while True :
		while not paused and last_checked_date<datetime.now() :
			sleep(1)
			for thread in threads :
				if not thread.is_alive() :
					#if thread.exception is not None :
					#	on_error(*[thread.exception]+on_error_parameters)
					threads.remove(thread)
			for task in tasks :
				if datetime.now()>=task.execution_time and task.to_be_executed :
					threads.append(Modern_Thread(target=task.callback_function, args=task.callback_parameters))
					threads[-1].start()
					task.to_be_executed=False
					#task.callback_function(*task.callback_parameters)
					if task.repetitive and task.repeat_times_left>0 :
						task.repeat_times_left-=1
						task.update_execution_time()
					else :
						task.destroy()
task_execute_thread=Thread(target=task_executer)
def load_str_tasks(strtasks) :
	if strtasks is None : strtasks=[]
	else : strtasks=pickle.loads(strtasks)
	for i in strtasks :
		Task(i)
def start() :
	global paused
	paused=False
	task_execute_thread.start()

class Modern_Thread(Thread) :
	def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
		
		self.state="idle"
		self.exception=None
		self.handle_exception=True
		def ass(self : Modern_Thread, target, args) :
			try :
				target(*args)
			except Exception as e :
				self.exception=e
				if self.handle_exception and on_error is not None :
					on_error(*[e]+on_error_parameters)
		super().__init__(group, ass, name, [self, target]+[args], kwargs, daemon=daemon)
	def start(self) :
		self.state="started"
		super().start()
	def join(self) :
		super().join()
		self.state="finished"




class Task :
	def __init__(self, str_repr=None, callback_function=None, callback_parameters=None, execution_time=None, relative_execution_time=None, repetitive=False, repeat_times_left=0, fail_limit=None) :
		if str_repr is None :
			assert not (execution_time is None and relative_execution_time is None) and None in (execution_time, relative_execution_time)
			self.relative_execution_time=relative_execution_time
			self.callback_function=callback_function
			if relative_execution_time is not None :
				execution_time=datetime.now().replace(microsecond=0)+self.evaluate_execution_timedelta()
			self.execution_time=execution_time
			self.callback_parameters=callback_parameters
			self.repeat_times_left=repeat_times_left-1
			self.repetitive=repetitive
			if fail_limit is not None :
				self.fail_limiter=True
				self.fail_limit=fail_limit
			else :
				self.fail_limit=0
		else :
			self=pickle.loads(str_repr)
		self.to_be_executed=True
		tasks.append(self)
	def parse_to_str(self) :
		return pickle.dumps(self)
	def evaluate_execution_timedelta(self) :
		if "!" in self.relative_execution_time :
			pp=randint(int(self.relative_execution_time.split("!")[0].split(",")[0]), int(self.relative_execution_time.split("!")[0].split(",")[1]))
			evaluatedrelative_execution_time=str(pp)+self.relative_execution_time.split("!")[1]
		else : evaluatedrelative_execution_time=self.relative_execution_time
		return parse_timedelta_from_string(evaluatedrelative_execution_time)
	def update_execution_time(self) :
		self.execution_time+=self.evaluate_execution_timedelta()
		self.to_be_executed=True
	def destroy(self) :
		tasks.remove(self)

tasks : List[Task]=[]
threads : List[Modern_Thread] = []


start()