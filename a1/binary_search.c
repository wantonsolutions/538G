#include <stdio.h>
#include <assert.h>

int main () {
    int array[] = {1,2,5,7,9,10};
    int i = 0;
    for (i = 0; i < sizeof(array)/sizeof(int)-1; i++){
        int index = binary_search(array, 0, sizeof(array)/sizeof(int), array[i]);
        printf("index of %d is %d\n",array[i],index);
    }

}

int binary_search(
	int arr[], int low, int high, int key) {
		assert (low > high || 0 <= low < high);
		while ( low <= high ) {
            //Find middle value
            int mid = low/2 + high/2;
            printf("low %d, mid =  %d, high=%d key=%d\n",low,mid,high,key);
            assert(0 <= mid);
            assert(mid <= high);
            int val = arr[mid];
            printf("low %d, mid =  %d, high=%d key=%d val=%d\n",low,mid,high,key,val);
            //Refine range
            if (key == val) { 
                return mid;
            }
            if (val > key) {
                high = mid-1;
            }
            else {
                low = mid+1;
            }
        }
	    return -1;
}

