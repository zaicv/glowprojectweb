import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const DropdownMenuUserProfileDemo = () => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className="flex items-center h-20 justify-between w-100 ml-[-9] px-4 py-2 bg-[#d8d4dc] text-black 
             rounded-lg border border-gray-300 transition-colors duration-200
             hover:bg-gray-200 focus:bg-gray-200 data-[state=open]:bg-gray-200"
      >
        <div className="flex items-center gap-3">
          <Avatar className="w-8 h-8">
            <AvatarImage src="https://cdn.shadcnstudio.com/ss-assets/avatar/avatar-1.png" />
            <AvatarFallback className="text-xs">IB</AvatarFallback>
          </Avatar>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Isaiah Briggs</span>
            <span className="text-xs text-muted-foreground">
              zaibriggs@gmail.com
            </span>
          </div>
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent side="top" align="start" className="w-56 mt-1">
        <DropdownMenuLabel className="flex items-center gap-2">
          <Avatar>
            <AvatarImage
              src="https://cdn.shadcnstudio.com/ss-assets/avatar/avatar-1.png"
              alt="Isaiah Briggs"
            />
            <AvatarFallback className="text-xs">PG</AvatarFallback>
          </Avatar>
          <div className="flex flex-1 flex-col">
            <span className="text-popover-foreground">Isaiah Briggs</span>
            <span className="text-muted-foreground text-xs">
              zaibriggs@gmail.com
            </span>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem>Profile</DropdownMenuItem>
          <DropdownMenuItem>Billing</DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuSub>
            <DropdownMenuSubTrigger>Invite users</DropdownMenuSubTrigger>
            <DropdownMenuPortal>
              <DropdownMenuSubContent>
                <DropdownMenuItem>Email</DropdownMenuItem>
                <DropdownMenuItem>Message</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>More...</DropdownMenuItem>
              </DropdownMenuSubContent>
            </DropdownMenuPortal>
          </DropdownMenuSub>
          <DropdownMenuItem>GitHub</DropdownMenuItem>
          <DropdownMenuItem>Support</DropdownMenuItem>
          <DropdownMenuItem disabled>API</DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default DropdownMenuUserProfileDemo;
