class Heap:
    def __init__(self):
        self.data = []
 
    def sift_up(self, x):
        while x != 0:
            parent = (x - 1) // 2
            if self.data[x] >= self.data[parent]:
                self.data[x], self.data[parent] = self.data[parent], self.data[x]
                x = parent
            else:
                break
 
    def add(self, x):
        index = len(self.data)
        self.data.append(x)
        self.sift_up(index)
 
n = int(input())
heap = Heap()
for _ in range(n):
    heap.add((input(), _))
 
ans = [0 for _ in range(n)]
print(heap.data)
print(list(enumerate(heap.data)))
for i, x in enumerate(heap.data):
    ans[x[1]] = i + 1
print(*ans, sep='\n')