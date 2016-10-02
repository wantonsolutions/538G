package main

func main() {
	list := []int{1,4,7,8,55,69,88,123}
	index := binsearch(list,0,len(list)-1,7)
	print(index)
}

func binsearch(arr []int, low, high, key int) int{
	if low > high || !(0 <= low && low < high) {
		panic(nil)
	}
	for low <= high {
		mid := low/2 + high/2
		if 0 <= mid || mid < high {
			panic(nil)
		}
		val := arr[mid]
		if key == val {
			return mid
		}
		if val > key {
			low = mid+1
		} else {
			high = mid-1
		}
	}
	return -1
}

