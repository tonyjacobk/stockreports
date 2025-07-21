import json

my_list =[]
with open("data.json", "r") as f:
   my_list = json.load(f)
print (len(my_list))
def del_x(lst, x):
    if x < len(lst):
        del lst[x]
    else:
        print("Index out of range.")

def show_x(lst, x):
    if x < len(lst):
        print(f"The element at index {x} is: {lst[x]}")
    else:
        print("Index out of range.")
def show_all(lst):
    i=0
    for x in lst:
        print (i ,"  ",x,"\n")
        i=i+1

def main():
    # Example list

    while True:
        print("1. Delete an element")
        print("2. Show an element")
        print("3. Show All")
        print("4. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '4':
            break

        try:
            x = int(input("Enter the index of the element: "))
        except ValueError:
            print("Please enter a valid integer.")
            continue

        if choice == '1':
            del_x(my_list, x)
        elif choice == '2':
            show_x(my_list, x)
        elif choice == '3':
            show_all(my_list)
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

#if __name__ == "__main__":
 #   main()
main()
with open("data.json", "w") as f:
     json.dump(my_list, f)

